"""Approval kind Change: VO follows the decision. Never a Payment Entry."""

from __future__ import annotations

from erpatlas.approvals.queue import APPROVED, REJECTED
from erpatlas.change_control.flow import APPROVED as VO_APPROVED
from erpatlas.change_control.flow import REJECTED as VO_REJECTED


def on_change(approval: dict, decision: str) -> str | None:
	name = approval.get("ref_name")
	if not name:
		return "Change has no row."
	import frappe
	doc = frappe.get_doc("Atlas Change Item", name)
	if decision == APPROVED:
		doc.status = VO_APPROVED
	elif decision == REJECTED:
		doc.status = VO_REJECTED
	else:
		return None
	doc.save(ignore_permissions=True)
	return None
