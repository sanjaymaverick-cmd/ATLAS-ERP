"""Possession gates. No frappe. Never writes Unit status — lock_adapter does."""

from __future__ import annotations

from erpatlas.booking.plan import ACTIVE, POSSESSION
from erpatlas.books.payment_gst import money
from erpatlas.property_inventory.lock import BOOKED, SOLD

OC_PENDING = "Pending"
OC_RECEIVED = "Received"
OC_STATUSES = (OC_PENDING, OC_RECEIVED)

HANDOVER_SNAGGING = "Snagging"
HANDOVER_POSSESSION = "Possession"
HANDOVER_SOCIETY = "Society"
HANDOVER_DEFECT = "Defect"
HANDOVER_STATUSES = (HANDOVER_SNAGGING, HANDOVER_POSSESSION, HANDOVER_SOCIETY, HANDOVER_DEFECT)

SNAG_OPEN = "Open"
SNAG_CLOSED = "Closed"


def refuse_possession(
	*,
	occupancy_certificate: str | None,
	open_snags: int,
	plan_collected,
	plan_gross,
	booking_status: str | None,
	unit_status: str | None,
) -> str | None:
	if booking_status == POSSESSION or unit_status == SOLD:
		return "Possession is already recorded."
	if booking_status != ACTIVE:
		return "Only an Active booking can take possession."
	if unit_status != BOOKED:
		return f"Unit is {unit_status} and cannot take possession."
	if occupancy_certificate != OC_RECEIVED:
		return "Occupancy Certificate must be received before possession."
	if int(open_snags or 0) > 0:
		n = int(open_snags)
		return f"{n} snag(s) still open — close them before possession."
	if money(plan_collected or 0) < money(plan_gross or 0):
		return "Possession requires the payment plan to be fully collected."
	return None


def possession_effects() -> dict:
	return {
		"unit_to": SOLD,
		"booking_to": POSSESSION,
		"handover_to": HANDOVER_POSSESSION,
	}


def open_snag_count(snags) -> int:
	return sum(1 for s in snags if s.get("status") == SNAG_OPEN)
