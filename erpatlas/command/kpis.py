"""Command calculators. No frappe. Never posts money or decisions."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable, Mapping

from erpatlas.approvals.queue import PENDING
from erpatlas.booking.plan import (
	ACTIVE,
	COMMISSION_ACCRUED,
	COMMISSION_APPROVED,
	POSSESSION,
)
from erpatlas.books.payment_gst import money
from erpatlas.property_inventory.lock import (
	CHANNEL_ROLES,
	HOLD_BOOKED,
	HOLD_EXPIRED,
	HOLD_HELD,
	HOLD_RELEASED,
	UNIT_STATUSES,
)

LIVE_BOOKING_STATUSES = frozenset({ACTIVE, POSSESSION})
COMMISSION_LIABILITY = frozenset({COMMISSION_ACCRUED, COMMISSION_APPROVED})

COMMAND_ROLES = frozenset({"Atlas Developer Admin", "Atlas Project Director"})

# P2 will read these from Atlas Settings. P0 uses closed defaults.
DEFAULT_APPROVAL_SLA_DAYS = 3
DEFAULT_HOLD_EXPIRING_DAYS = 2
EXCEPTION_LIMIT = 15


def refuse_command_access(roles: Iterable[str]) -> str | None:
	role_set = set(roles)
	if role_set & CHANNEL_ROLES:
		return "Channel seats cannot open Command."
	if not role_set & COMMAND_ROLES:
		return "Command is for Atlas Developer Admin and Atlas Project Director."
	return None


def add_iso_days(today: str, days: int) -> str:
	return (date.fromisoformat(today) + timedelta(days=days)).isoformat()


def filter_by_projects(rows: Iterable[Mapping], project_names: set[str] | None) -> list[dict]:
	items = [dict(r) for r in rows]
	if project_names is None:
		return items
	return [r for r in items if r.get("project") in project_names]


def count_units_by_status(units: Iterable[Mapping]) -> dict[str, int]:
	counts = {status: 0 for status in UNIT_STATUSES}
	for unit in units:
		status = unit.get("status")
		if status in counts:
			counts[status] += 1
	return counts


def aging_days_of(row: Mapping, today: str) -> int:
	if row.get("aging_days") not in (None, ""):
		return int(row["aging_days"])
	created = str(row.get("creation") or "")[:10]
	if not created:
		return 0
	return (date.fromisoformat(today) - date.fromisoformat(created)).days


def live_holds(holds: Iterable[Mapping]) -> list[dict]:
	return [dict(h) for h in holds if h.get("status") == HOLD_HELD]


def holds_expiring_soon(holds: Iterable[Mapping], today: str, within_days: int) -> list[dict]:
	"""Held rows whose inclusive `until` falls between today and today+within_days."""
	end = add_iso_days(today, within_days)
	out = []
	for hold in live_holds(holds):
		until = hold.get("until")
		if until and today <= str(until) <= end:
			out.append(hold)
	return out


def approval_aging(approvals: Iterable[Mapping], today: str, sla_days: int) -> dict:
	pending = []
	for row in approvals:
		if row.get("status") != PENDING:
			continue
		item = dict(row)
		item["aging_days"] = aging_days_of(item, today)
		pending.append(item)
	past = [a for a in pending if a["aging_days"] >= sla_days]
	oldest = max((a["aging_days"] for a in pending), default=0)
	return {
		"pending": len(pending),
		"past_sla": len(past),
		"oldest_days": oldest,
		"pending_rows": pending,
	}


def exception_queue(pending_rows: Iterable[Mapping], *, limit: int = EXCEPTION_LIMIT) -> list[dict]:
	ordered = sorted(pending_rows, key=lambda a: int(a.get("aging_days") or 0), reverse=True)
	return [dict(a) for a in ordered[:limit]]


def _iso_month(value) -> str:
	return str(value or "")[:7]


def money_kpis(
	*,
	bookings: Iterable[Mapping],
	steps: Iterable[Mapping],
	payments: Iterable[Mapping],
	commissions: Iterable[Mapping],
	holds: Iterable[Mapping],
	today: str,
) -> dict:
	"""Booking / PE / commission totals. Not bank cash, not runway."""
	month = today[:7]
	live = [dict(b) for b in bookings if b.get("status") in LIVE_BOOKING_STATUSES]
	mtd_bookings = [b for b in live if _iso_month(b.get("creation")) == month]
	booking_value_live = money(0)
	booking_value_mtd = money(0)
	collected_live = money(0)
	for row in live:
		booking_value_live += money(row.get("total_consideration") or 0)
		collected_live += money(row.get("collected") or 0)
	for row in mtd_bookings:
		booking_value_mtd += money(row.get("total_consideration") or 0)

	plan_gross = money(0)
	plan_collected = money(0)
	live_names = {b.get("name") for b in live if b.get("name")}
	step_rows = [
		s
		for s in steps
		if not s.get("parent") or not live_names or s.get("parent") in live_names
	]
	if step_rows:
		for step in step_rows:
			plan_gross += money(step.get("gross") or 0)
			plan_collected += money(step.get("collected") or 0)
	else:
		plan_gross = booking_value_live
		plan_collected = collected_live

	collections_mtd = money(0)
	for pe in payments:
		if _iso_month(pe.get("posting_date")) == month:
			collections_mtd += money(pe.get("paid_amount") or pe.get("amount") or 0)

	liability = money(0)
	for comm in commissions:
		if comm.get("status") in COMMISSION_LIABILITY:
			liability += money(comm.get("amount") or 0)

	closed = 0
	converted = 0
	for hold in holds:
		status = hold.get("status")
		if status == HOLD_BOOKED:
			converted += 1
			closed += 1
		elif status in (HOLD_RELEASED, HOLD_EXPIRED):
			closed += 1
	conversion = None
	if closed:
		conversion = money(converted * 100 / closed)

	channel = 0
	in_house = 0
	for row in live:
		if row.get("channel_company"):
			channel += 1
		else:
			in_house += 1

	return {
		"booking_value_live": booking_value_live,
		"booking_value_mtd": booking_value_mtd,
		"collections_mtd": collections_mtd,
		"plan_gross": plan_gross,
		"plan_collected": plan_collected,
		"receivable": money(plan_gross - plan_collected),
		"commission_liability": liability,
		"hold_conversion_pct": conversion,
		"channel_bookings": channel,
		"in_house_bookings": in_house,
		"live_bookings": len(live),
	}


def build_command(
	*,
	units: Iterable[Mapping],
	holds: Iterable[Mapping],
	approvals: Iterable[Mapping],
	today: str,
	project_names: set[str] | None = None,
	sla_days: int = DEFAULT_APPROVAL_SLA_DAYS,
	hold_expiring_days: int = DEFAULT_HOLD_EXPIRING_DAYS,
	bookings: Iterable[Mapping] = (),
	steps: Iterable[Mapping] = (),
	payments: Iterable[Mapping] = (),
	commissions: Iterable[Mapping] = (),
	handovers: Iterable[Mapping] = (),
	snags: Iterable[Mapping] = (),
	vendors: Iterable[Mapping] = (),
	thresholds: Mapping | None = None,
) -> dict:
	"""Exception-first payload. Booking money is P1. Bank cash/runway is not."""
	units_f = filter_by_projects(units, project_names)
	holds_f = filter_by_projects(holds, project_names)
	approvals_f = filter_by_projects(approvals, project_names)
	bookings_f = filter_by_projects(bookings, project_names)
	steps_f = filter_by_projects(steps, project_names)
	payments_f = filter_by_projects(payments, project_names)
	commissions_f = filter_by_projects(commissions, project_names)
	aging = approval_aging(approvals_f, today, sla_days)
	held = live_holds(holds_f)
	expiring = holds_expiring_soon(holds_f, today, hold_expiring_days)
	money_board = money_kpis(
		bookings=bookings_f,
		steps=steps_f,
		payments=payments_f,
		commissions=commissions_f,
		holds=holds_f,
		today=today,
	)
	from erpatlas.command.risk import DEFAULT_THRESHOLDS, risk_cards

	th = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
	risk = risk_cards(
		holds=holds_f,
		approvals=approvals_f,
		bookings=bookings_f,
		money_board=money_board,
		handovers=filter_by_projects(handovers, project_names),
		snags=filter_by_projects(snags, project_names),
		vendors=vendors,
		today=today,
		thresholds=th,
	)
	return {
		"units": count_units_by_status(units_f),
		"holds": {
			"held": len(held),
			"expiring_soon": len(expiring),
			"conversion_pct": money_board["hold_conversion_pct"],
		},
		"approvals": {
			"pending": aging["pending"],
			"past_sla": aging["past_sla"],
			"oldest_days": aging["oldest_days"],
			"sla_days": sla_days,
		},
		"exceptions": exception_queue(aging["pending_rows"]),
		"money": money_board,
		"risk": risk,
		"thresholds": th,
		"shows_money": True,
		"shows_cash": False,
	}
