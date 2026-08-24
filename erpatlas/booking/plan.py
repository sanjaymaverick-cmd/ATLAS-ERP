"""Booking plan, activate/collect/cancel refusals, commission accrual.

Do not import frappe here. Books posting lives in books.posting + booking.activate.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Iterable, Mapping

from erpatlas.books.payment_gst import (
	expand_schedule,
	money,
	next_unpaid,
	refuse_collect as gst_refuse_collect,
)
from erpatlas.property_inventory.lock import BOOKED, LIVE_BOOKING, SOLD, refuse_book

DRAFT = "Draft"
ACTIVE = "Active"
CANCELLED = "Cancelled"
POSSESSION = "Possession"
BOOKING_STATUSES = (DRAFT, ACTIVE, CANCELLED, POSSESSION)

HOLD_BOOKED = "Booked"
STEP_KINDS = ("booking", "slab", "possession")

COMMISSION_ACCRUED = "Accrued"
COMMISSION_APPROVED = "Approved"
COMMISSION_PAID = "Paid"
COMMISSION_REJECTED = "Rejected"
CHANNEL_ACTIVE = "Active"


def default_steps() -> list[dict]:
	return [{"label": "Consideration", "kind": "booking", "percent": "100"}]


def refuse_step_percents(steps: Iterable[Mapping] | None) -> str | None:
	rows = list(steps or [])
	if not rows:
		return "Payment schedule needs at least one step."
	try:
		pct_sum = sum(Decimal(str(s["percent"])) for s in rows)
	except Exception:
		return "Payment step percents must sum to 100."
	if pct_sum != Decimal("100"):
		return "Payment step percents must sum to 100."
	return None


def booking_live_unit(*, status: str, unit: str, booking_name: str | None = None) -> str | None:
	"""Unique key: the unit name while the booking is live, otherwise this booking's name."""
	if status in LIVE_BOOKING and unit:
		return unit
	return booking_name


def refuse_activate(
	*,
	unit_status: str | None,
	code: str,
	live_booking: bool,
	customer: str | None,
	consideration,
	steps: Iterable[Mapping] | None,
	booking_status: str = DRAFT,
) -> str | None:
	if booking_status == ACTIVE:
		return "Booking is already Active."
	if booking_status == CANCELLED:
		return "Cancelled booking cannot activate."
	if booking_status == POSSESSION:
		return "Possession booking cannot activate."
	if not customer:
		return "Booking needs a customer."
	try:
		if money(consideration) <= 0:
			return "Booking consideration must be greater than zero."
	except Exception:
		return "Booking consideration must be greater than zero."
	err = refuse_book(status=unit_status, code=code, live_booking=live_booking)
	if err:
		return err
	return refuse_step_percents(steps)


def refuse_collect_booking(
	*,
	status: str,
	step: Mapping | None,
	receipt,
	plan_collected,
	plan_gross,
) -> str | None:
	if status == CANCELLED:
		return "Cancelled booking cannot collect."
	if status not in (ACTIVE, POSSESSION):
		return "Only an Active booking can collect."
	if not step:
		return "Payment plan is already collected."
	return gst_refuse_collect(
		step_gross=step["gross"],
		already_collected=step.get("collected") or 0,
		receipt=receipt,
		plan_collected=plan_collected,
		plan_gross=plan_gross,
	)


def commission_amount(consideration, rate):
	return money(money(consideration) * Decimal(str(rate)) / Decimal("100"))


def accrue_intent(
	*,
	channel_company: str | None,
	channel_status: str | None,
	rate,
	consideration,
	already_accrued: bool,
) -> dict | None:
	"""Commission row to insert, or None. Never a Payment Entry."""
	if already_accrued:
		return None
	if not channel_company:
		return None
	if channel_status != CHANNEL_ACTIVE:
		return None
	if rate is None or Decimal(str(rate)) <= 0:
		return None
	return {
		"amount": commission_amount(consideration, rate),
		"status": COMMISSION_ACCRUED,
		"creates_payment_entry": False,
	}


def refuse_cancel(*, status: str, unit_status: str | None, has_posted_money: bool) -> str | None:
	if status == POSSESSION or unit_status == SOLD:
		return "Possession bookings cannot cancel."
	if status != ACTIVE:
		return "Only an Active booking can cancel."
	if has_posted_money:
		return "Money exists on this booking. Finance must credit-note or refund first."
	return None


def channel_may_read_unit(*, status: str, own_hold: bool, own_booking: bool) -> bool:
	from erpatlas.property_inventory.lock import AVAILABLE

	if status == AVAILABLE:
		return True
	return bool(own_hold or own_booking)


def activate_plan(*, consideration, steps: Iterable[Mapping], rate, tax_included: str) -> dict:
	err = refuse_step_percents(steps)
	if err:
		raise ValueError(err)
	expanded = expand_schedule(
		consideration=consideration, steps=steps, rate=rate, tax_included=tax_included
	)
	grand = money(0)
	taxable = money(0)
	for step in expanded:
		grand += step["gross"]
		taxable += step["taxable"]
	return {
		"unit_to": BOOKED,
		"hold_to": HOLD_BOOKED,
		"booking_status": ACTIVE,
		"steps": expanded,
		"grand_total": grand,
		"taxable_total": taxable,
	}


def next_collect_step(steps: Iterable[Mapping]) -> dict | None:
	return next_unpaid(steps)
