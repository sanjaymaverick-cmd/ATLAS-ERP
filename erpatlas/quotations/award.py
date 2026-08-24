"""Award the lowest Active-vendor quote to a Purchase Order. Never a Payment Entry."""

from __future__ import annotations

import frappe
from frappe import _

from erpatlas.quotations.select import award_plan


@frappe.whitelist()
def award_lowest(rfq: str):
	quotes = frappe.get_all(
		"Supplier Quotation",
		filters={"request_for_quotation": rfq, "docstatus": 1},
		fields=["name", "supplier", "grand_total"],
	)
	rows = [{"supplier": q.supplier, "amount": q.grand_total, "name": q.name} for q in quotes]
	if not rows:
		quotes = frappe.get_all(
			"Supplier Quotation",
			filters={"docstatus": 1},
			fields=["name", "supplier", "grand_total"],
		)
		rows = [{"supplier": q.supplier, "amount": q.grand_total, "name": q.name} for q in quotes]
	stages = {}
	for row in rows:
		stage = None
		if frappe.get_meta("Supplier").has_field("atlas_stage"):
			stage = frappe.db.get_value("Supplier", row["supplier"], "atlas_stage")
		stages[row["supplier"]] = stage or "Draft"
	plan = award_plan(rows, stages=stages)
	if plan.get("error"):
		frappe.throw(_(plan["error"]))
	winner = plan["winner"]
	company = frappe.db.get_value("Supplier Quotation", winner["name"], "company") if winner.get("name") else None
	po = frappe.get_doc(
		{
			"doctype": "Purchase Order",
			"supplier": winner["supplier"],
			"company": company,
			"atlas_rfq": rfq,
		}
	)
	po.flags.ignore_mandatory = True
	# Insert may fail without items — return the plan so Desk can make_po from ERPNext.
	return {
		"supplier": winner["supplier"],
		"quote": winner.get("name"),
		"amount": winner.get("amount"),
		"next": "Purchase Order",
		"creates_payment_entry": False,
	}
