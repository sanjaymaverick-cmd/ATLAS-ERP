"""Unit status lock. Callers pass facts; this module decides refusal.

Database compare-and-swap lives in lock_adapter. Do not import frappe here.
"""

from __future__ import annotations

from typing import Iterable

AVAILABLE = "Available"
HELD = "Held"
BOOKED = "Booked"
SOLD = "Sold"
CANCELLED = "Cancelled"
DISPUTE = "Dispute"

UNIT_STATUSES = (AVAILABLE, HELD, BOOKED, SOLD, CANCELLED, DISPUTE)
HOLDABLE = frozenset({AVAILABLE})
BOOKABLE = frozenset({AVAILABLE, HELD})
LIVE_BOOKING = frozenset({"Active", "Possession"})
DISPUTABLE = frozenset({AVAILABLE, HELD, BOOKED})

HOLD_HELD = "Held"
HOLD_BOOKED = "Booked"
HOLD_EXPIRED = "Expired"
HOLD_RELEASED = "Released"
HOLD_STATUSES = (HOLD_HELD, HOLD_BOOKED, HOLD_EXPIRED, HOLD_RELEASED)

CHANNEL_ROLES = frozenset({"Atlas Channel Agent", "Atlas Channel Admin"})

# (from, to) → reason tag. Anything else is refused.
TRANSITIONS: dict[tuple[str, str], str] = {
	(AVAILABLE, HELD): "hold",
	(AVAILABLE, BOOKED): "book",
	(AVAILABLE, DISPUTE): "dispute",
	(HELD, AVAILABLE): "release_or_expire",
	(HELD, BOOKED): "book",
	(HELD, DISPUTE): "dispute",
	(BOOKED, SOLD): "possession",
	(BOOKED, AVAILABLE): "cancel_booking",
	(BOOKED, DISPUTE): "dispute",
}


def refuse_transition(frm: str, to: str) -> str | None:
	if frm == to:
		return None
	if (frm, to) not in TRANSITIONS:
		return f"Cannot move a unit from {frm} to {to}."
	return None


def refuse_hold(*, status: str | None, code: str) -> str | None:
	if not status:
		return "Unit not found."
	if status not in HOLDABLE:
		return f"Unit {code} is {status} — hold refused."
	return None


def refuse_book(*, status: str | None, code: str, live_booking: bool) -> str | None:
	if live_booking:
		return f"Unit {code} already has an active booking."
	if status and status not in BOOKABLE:
		return f"Unit {code} is {status} and cannot be booked."
	return None


def refuse_hold_without_report(*, roles: Iterable[str], has_today_report: bool) -> str | None:
	role_set = set(roles)
	if not role_set & CHANNEL_ROLES:
		return None
	if not has_today_report:
		return "File today’s daily report before placing a hold."
	return None


def refuse_dispute(*, status: str | None, code: str, roles: Iterable[str]) -> str | None:
	if not status:
		return "Unit not found."
	if set(roles) & CHANNEL_ROLES:
		return "Channel seats cannot mark a dispute."
	if status not in DISPUTABLE:
		return f"Unit {code} is {status} and cannot be marked dispute."
	return None


def live_unit_key(*, status: str, unit: str, hold_name: str | None = None) -> str | None:
	"""Unique key: the unit name while Held (one live hold), otherwise this hold's name."""
	if status == HOLD_HELD and unit:
		return unit
	return hold_name


def holds_due_to_expire(holds: Iterable[dict], today: str) -> list[dict]:
	"""`until` is inclusive: the hold is live through that calendar day."""
	return [h for h in holds if h.get("status") == HOLD_HELD and h.get("until") and h["until"] < today]


def unit_status_on_hold_expire(unit_status: str) -> str | None:
	"""Atlas-3 expireHolds always forced Available and could unlock a booked unit. Only move if still Held."""
	if unit_status == HELD:
		return AVAILABLE
	return None


def channel_needs_booking_approval(channel_company: str | None) -> bool:
	return bool(channel_company)
