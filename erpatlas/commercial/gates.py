"""PO cannot be issued until the vendor is Active. Full Commercial module ships later."""

from __future__ import annotations


def validate_vendor_active(doc, method=None):
	import frappe

	supplier = doc.get("supplier")
	if not supplier:
		return
	stage = frappe.db.get_value("Supplier", supplier, "atlas_stage")
	if stage is None:
		# Custom field not installed yet — do not block vanilla ERPNext POs
		# until Commercial ships atlas_stage on Supplier.
		return
	if stage != "Active":
		frappe.throw("Purchase orders cannot be issued until the vendor is Active.")
