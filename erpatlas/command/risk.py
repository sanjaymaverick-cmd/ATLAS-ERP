"""Deterministic Command risk cards. No frappe. Never auto-approve, pay, or lock."""

from __future__ import annotations

from typing import Iterable, Mapping

from erpatlas.approvals.queue import MONEY_KINDS, PENDING
from erpatlas.books.payment_gst import money
from erpatlas.command.kpis import (
	DEFAULT_APPROVAL_SLA_DAYS,
	DEFAULT_HOLD_EXPIRING_DAYS,
	LIVE_BOOKING_STATUSES,
	aging_days_of,
	holds_expiring_soon,
	live_holds,
)
from erpatlas.handover.gates import HANDOVER_SNAGGING, OC_PENDING, SNAG_OPEN
from erpatlas.property_inventory.lock import HOLD_EXPIRED

RED = "red"
AMBER = "amber"
RISK_LIMIT = 5

DEFAULT_THRESHOLDS = {
	"approval_sla_days": DEFAULT_APPROVAL_SLA_DAYS,
	"hold_expiring_days": DEFAULT_HOLD_EXPIRING_DAYS,
	"hold_without_book_days": 7,
	"collection_lag_percent": 20,
	"channel_concentration_percent": 70,
}


def _card(
	*,
	domain: str,
	severity: str,
	title: str,
	driver: str,
	waiting_on: str | None = None,
	doctype: str | None = None,
	refs: list | None = None,
) -> dict:
	return {
		"domain": domain,
		"severity": severity,
		"title": title,
		"driver": driver,
		"waiting_on": waiting_on,
		"doctype": doctype,
		"refs": refs or [],
		"auto_action": False,
	}


def rank_cards(cards: Iterable[Mapping], *, limit: int = RISK_LIMIT) -> list[dict]:
	order = {RED: 0, AMBER: 1}
	ranked = sorted(
		(dict(c) for c in cards),
		key=lambda c: (order.get(c.get("severity"), 9), -len(c.get("refs") or [])),
	)
	return ranked[:limit]


def risk_cards(
	*,
	holds: Iterable[Mapping],
	approvals: Iterable[Mapping],
	bookings: Iterable[Mapping],
	money_board: Mapping,
	handovers: Iterable[Mapping] = (),
	snags: Iterable[Mapping] = (),
	vendors: Iterable[Mapping] = (),
	today: str,
	thresholds: Mapping | None = None,
) -> list[dict]:
	t = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
	cards: list[dict] = []
	cards.extend(_approval_stall(approvals, today, int(t["approval_sla_days"])))
	cards.extend(_sales_holds(holds, today, int(t["hold_without_book_days"]), int(t["hold_expiring_days"])))
	cards.extend(_channel_concentration(bookings, float(t["channel_concentration_percent"])))
	cards.extend(_collection_lag(money_board, float(t["collection_lag_percent"])))
	cards.extend(_delivery(handovers, snags))
	cards.extend(_commercial_vendors(vendors))
	return rank_cards(cards)


def _approval_stall(approvals, today: str, sla_days: int) -> list[dict]:
	stale = []
	for row in approvals:
		if row.get("status") != PENDING:
			continue
		if row.get("kind") not in MONEY_KINDS:
			continue
		days = aging_days_of(row, today)
		if days >= sla_days:
			item = dict(row)
			item["aging_days"] = days
			stale.append(item)
	if not stale:
		return []
	oldest = max(stale, key=lambda r: int(r.get("aging_days") or 0))
	return [
		_card(
			domain="Approval stall",
			severity=RED,
			title=f"{len(stale)} money Approval(s) past {sla_days} days",
			driver=f"Oldest: {oldest.get('title') or oldest.get('name')} · {oldest.get('aging_days')}d · {oldest.get('kind')}.",
			waiting_on=oldest.get("waiting_on"),
			doctype="Atlas Approval",
			refs=[r.get("name") for r in stale if r.get("name")],
		)
	]


def _sales_holds(holds, today: str, without_book_days: int, expiring_days: int) -> list[dict]:
	out = []
	expired = [dict(h) for h in holds if h.get("status") == HOLD_EXPIRED]
	if expired:
		out.append(
			_card(
				domain="Sales",
				severity=AMBER,
				title=f"{len(expired)} hold(s) expired without a booking",
				driver="Hold expiry returns the unit to Available only if it is still Held.",
				waiting_on="Sales Manager / MD",
				doctype="Atlas Unit Hold",
				refs=[h.get("name") for h in expired if h.get("name")],
			)
		)
	stuck = []
	for hold in live_holds(holds):
		days = aging_days_of(hold, today)
		if days >= without_book_days:
			stuck.append(hold)
	if stuck:
		out.append(
			_card(
				domain="Sales",
				severity=RED,
				title=f"{len(stuck)} unit(s) held without a booking for {without_book_days}+ days",
				driver="A live Hold is not a Booking. Convert or release before the unit goes stale.",
				waiting_on="Sales Manager / MD",
				doctype="Atlas Unit Hold",
				refs=[h.get("name") for h in stuck if h.get("name")],
			)
		)
	expiring = holds_expiring_soon(holds, today, expiring_days)
	if expiring:
		out.append(
			_card(
				domain="Sales",
				severity=AMBER,
				title=f"{len(expiring)} hold(s) expiring within {expiring_days} day(s)",
				driver="until is inclusive — the hold is live through that calendar day.",
				waiting_on="Sales Manager / MD",
				doctype="Atlas Unit Hold",
				refs=[h.get("name") for h in expiring if h.get("name")],
			)
		)
	return out


def _channel_concentration(bookings, percent_limit) -> list[dict]:
	live = [b for b in bookings if b.get("status") in LIVE_BOOKING_STATUSES]
	if len(live) < 2:
		return []
	channel = sum(1 for b in live if b.get("channel_company"))
	pct = money(channel * 100 / len(live))
	if pct < money(percent_limit):
		return []
	return [
		_card(
			domain="Sales",
			severity=AMBER,
			title=f"Channel mix {pct}% of live bookings",
			driver=f"{channel} of {len(live)} live bookings are Channel Company. Threshold is {percent_limit}%.",
			waiting_on="Sales Manager / MD",
			doctype="Atlas Booking",
			refs=[b.get("name") for b in live if b.get("channel_company") and b.get("name")],
		)
	]


def _collection_lag(money_board: Mapping, percent_limit) -> list[dict]:
	plan = money(money_board.get("plan_gross") or 0)
	if plan <= 0:
		return []
	receivable = money(money_board.get("receivable") or 0)
	pct = money(receivable * 100 / plan)
	if pct < money(percent_limit):
		return []
	severity = RED if pct >= money(50) else AMBER
	return [
		_card(
			domain="Liquidity",
			severity=severity,
			title=f"Collection lag {pct}% of the payment plan",
			driver=f"Receivable {receivable} against plan {plan}. Not bank cash.",
			waiting_on="Finance Lead",
			doctype="Atlas Booking",
			refs=[],
		)
	]


def _delivery(handovers, snags) -> list[dict]:
	out = []
	open_snags = [s for s in snags if s.get("status") == SNAG_OPEN]
	if open_snags:
		out.append(
			_card(
				domain="Delivery",
				severity=RED,
				title=f"{len(open_snags)} snag(s) still open",
				driver="Possession is blocked until snags are closed and Occupancy Certificate is received.",
				waiting_on="Project Director",
				doctype="Atlas Snag",
				refs=[s.get("name") for s in open_snags if s.get("name")],
			)
		)
	pending_oc = [
		h
		for h in handovers
		if h.get("status") == HANDOVER_SNAGGING and h.get("occupancy_certificate") == OC_PENDING
	]
	if pending_oc:
		out.append(
			_card(
				domain="Delivery",
				severity=AMBER,
				title=f"{len(pending_oc)} handover(s) waiting on Occupancy Certificate",
				driver="Keys wait for Occupancy Certificate. Chip stays in plain English.",
				waiting_on="Project Director",
				doctype="Atlas Handover Case",
				refs=[h.get("name") for h in pending_oc if h.get("name")],
			)
		)
	return out


def _commercial_vendors(vendors) -> list[dict]:
	blocked = [v for v in vendors if (v.get("atlas_stage") or "Draft") != "Active"]
	if not blocked:
		return []
	return [
		_card(
			domain="Commercial",
			severity=AMBER,
			title=f"{len(blocked)} vendor(s) not Active",
			driver="No Purchase Order until the vendor is Active (GSTIN required).",
			waiting_on="Project Director",
			doctype="Supplier",
			refs=[v.get("name") for v in blocked if v.get("name")],
		)
	]
