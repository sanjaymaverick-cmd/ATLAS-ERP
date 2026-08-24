from __future__ import annotations

import frappe
from frappe import _

from erpatlas.commercial.vendor import VENDOR_APPROVAL, refuse_vendor_active


@frappe.whitelist()
def send_vendor_for_approval(supplier: str):
	doc = frappe.get_doc("Supplier", supplier)
	gstin = doc.get("gstin") or doc.get("tax_id")
	err = refuse_vendor_active(gstin=gstin)
	if err:
		frappe.throw(_(err))
	from erpatlas.approvals.intake import raise_approval

	if doc.meta.has_field("atlas_stage"):
		doc.atlas_stage = VENDOR_APPROVAL
		doc.save()
	name = raise_approval(
		kind="Vendor",
		title=f"Vendor · {doc.supplier_name or doc.name}",
		project=_any_project(doc),
		waiting_on="Project Director",
		ref_doctype="Supplier",
		ref_name=doc.name,
		context="GSTIN recorded. Active after Approval. No PO until then.",
	)
	return {"approval": name}


def _any_project(supplier) -> str:
	company = supplier.get("default_company")
	filters = {"company": company} if company else {}
	name = frappe.db.get_value("Project", filters)
	if not name:
		frappe.throw(_("Vendor approval needs a Project on this Legal Entity."))
	return name
