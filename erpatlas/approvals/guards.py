"""Stop Payment Entry from being used as a silent commission payout."""

from __future__ import annotations


def refuse_commission_auto_pay(doc, method=None):
	import frappe

	from erpatlas.books.commission import refuse_payment_entry_for_commission

	if getattr(frappe.flags, "in_atlas_commission_payout", False):
		return
	voucher_type = None
	for row in doc.get("references") or []:
		if row.get("reference_doctype") == "Atlas Commission":
			voucher_type = "Atlas Commission"
			break
	err = refuse_payment_entry_for_commission(
		voucher_type=voucher_type,
		remarks=(doc.get("remarks") or "") + " " + (doc.get("reference_no") or ""),
	)
	if err:
		frappe.throw(err)
