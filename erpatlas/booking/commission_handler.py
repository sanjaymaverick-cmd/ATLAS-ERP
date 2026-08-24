"""Approval kind Commission: mark Approved / Rejected. Never a Payment Entry."""

from __future__ import annotations

from erpatlas.approvals.queue import APPROVED, REJECTED
from erpatlas.booking.plan import COMMISSION_APPROVED, COMMISSION_REJECTED


def on_commission(approval: dict, decision: str) -> str | None:
	import frappe

	name = approval.get("ref_name")
	if not name:
		return "Commission has no row."
	doc = frappe.get_doc("Atlas Commission", name)
	if decision == APPROVED:
		doc.status = COMMISSION_APPROVED
	elif decision == REJECTED:
		doc.status = COMMISSION_REJECTED
	else:
		return None
	frappe.flags.in_atlas_commission = True
	try:
		doc.save(ignore_permissions=True)
	finally:
		frappe.flags.in_atlas_commission = False
	return None
