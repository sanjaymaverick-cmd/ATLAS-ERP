"""Approval handler: partner hold → booking. Unit stays Held until Approved."""

from __future__ import annotations

from erpatlas.approvals.queue import APPROVED, REJECTED
from erpatlas.property_inventory.lock import HELD


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
	from erpatlas.booking.activate import activate_from_hold

	try:
		activate_from_hold(hold_name, consideration=approval.get("amount") or hold.booking_value)
	except frappe.ValidationError as e:
		return str(e)
	return None
