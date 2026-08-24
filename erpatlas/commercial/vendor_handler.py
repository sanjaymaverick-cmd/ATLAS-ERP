"""Approval kind Vendor: Supplier atlas_stage → Active. GSTIN required."""

from __future__ import annotations

from erpatlas.approvals.queue import APPROVED, REJECTED
from erpatlas.commercial.vendor import VENDOR_ACTIVE, VENDOR_APPROVAL, refuse_vendor_active


def on_vendor(approval: dict, decision: str) -> str | None:
	import frappe

	name = approval.get("ref_name")
	if not name:
		return "Vendor approval has no Supplier."
	if decision == REJECTED:
		if frappe.get_meta("Supplier").has_field("atlas_stage"):
			frappe.db.set_value("Supplier", name, "atlas_stage", VENDOR_APPROVAL)
		return None
	if decision != APPROVED:
		return None
	gstin = frappe.db.get_value("Supplier", name, "gstin") or frappe.db.get_value(
		"Supplier", name, "tax_id"
	)
	err = refuse_vendor_active(gstin=gstin)
	if err:
		return err
	if frappe.get_meta("Supplier").has_field("atlas_stage"):
		frappe.db.set_value("Supplier", name, "atlas_stage", VENDOR_ACTIVE)
	return None
