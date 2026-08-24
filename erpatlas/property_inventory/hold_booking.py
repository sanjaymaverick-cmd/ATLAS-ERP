"""Approval handler: partner hold → booking. Unit stays Held until Approved."""

from __future__ import annotations

from erpatlas.approvals.queue import APPROVED, REJECTED
from erpatlas.property_inventory.lock import BOOKED, HELD, HOLD_BOOKED, live_unit_key, refuse_book


def on_hold_booking(approval: dict, decision: str) -> str | None:
	import frappe

	hold_name = approval.get("ref_name")
	if not hold_name:
		return "Hold booking has no hold."
	hold = frappe.get_doc("Atlas Unit Hold", hold_name)
	if decision == REJECTED:
		hold.booking_requested = 0
		hold.booking_value = None
		hold.save(ignore_permissions=True)
		return None
	if decision != APPROVED:
		return None
	if hold.status != HELD:
		return "Hold not active."
	unit = frappe.get_doc("Atlas Unit", hold.unit)
	err = refuse_book(status=unit.status, code=unit.code, live_booking=unit.status == BOOKED)
	if err:
		return err
	from erpatlas.property_inventory.lock_adapter import try_set_status

	moved = try_set_status(unit.name, HELD, BOOKED, f"Hold booking {hold.name}")
	if moved:
		return moved
	hold.status = HOLD_BOOKED
	hold.booking_requested = 0
	hold.live_unit = live_unit_key(status=HOLD_BOOKED, unit=hold.unit, hold_name=hold.name)
	hold.save(ignore_permissions=True)
	return None
