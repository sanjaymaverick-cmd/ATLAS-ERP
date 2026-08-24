"""PO cannot be issued until the vendor is Active. Full Commercial module ships later."""

from __future__ import annotations


def validate_vendor_active(doc, method=None):
	import frappe

	from erpatlas.commercial.vendor import refuse_purchase_order

	supplier = doc.get("supplier")
	if not supplier:
		return
	if not frappe.get_meta("Supplier").has_field("atlas_stage"):
		return
	stage = frappe.db.get_value("Supplier", supplier, "atlas_stage")
	err = refuse_purchase_order(atlas_stage=stage or "Draft")
	if err:
		frappe.throw(err)
