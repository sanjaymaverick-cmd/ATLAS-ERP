"""Purchase Order waits for Approval. Submit happens only on Approved. Never a Payment Entry."""

from __future__ import annotations

from erpatlas.approvals.queue import APPROVED
from erpatlas.commercial.vendor import refuse_purchase_order


def refuse_submit_po(*, approved: bool, flagged: bool) -> str | None:
	if flagged:
		return None
	if approved:
		return None
	return "Purchase Order waits for a yes in Approvals."


def refuse_request_po(*, pending: bool, vendor_stage: str | None, already_submitted: bool) -> str | None:
	if already_submitted:
		return "This purchase order is already submitted."
	if pending:
		return "This purchase order is already waiting in Approvals."
	return refuse_purchase_order(atlas_stage=vendor_stage)


def raise_po_approval(po_name: str) -> dict:
	import frappe
	from frappe import _

	from erpatlas.approvals.intake import raise_approval

	po = frappe.get_doc("Purchase Order", po_name)
	stage = None
	if frappe.get_meta("Supplier").has_field("atlas_stage"):
		stage = frappe.db.get_value("Supplier", po.supplier, "atlas_stage")
	pending = bool(
		frappe.db.exists(
			"Atlas Approval",
			{"kind": "Purchase order", "ref_name": po.name, "status": "Pending"},
		)
	)
	err = refuse_request_po(
		pending=pending, vendor_stage=stage, already_submitted=po.docstatus == 1
	)
	if err:
		frappe.throw(_(err))
	amount = float(po.grand_total or po.total or 0)
	approval = raise_approval(
		kind="Purchase order",
		title=f"PO · {po.name} · {po.supplier}",
		project=po.project or _any_project(po),
		waiting_on="Managing Director",
		amount=amount,
		ref_doctype="Purchase Order",
		ref_name=po.name,
		context="Submit after a yes. Not a Payment Entry.",
	)
	if po.meta.has_field("atlas_approval"):
		po.db_set("atlas_approval", approval)
	return {"approval": approval, "creates_payment_entry": False}


def _any_project(po) -> str:
	import frappe
	from frappe import _

	if po.project:
		return po.project
	company = po.company
	name = frappe.db.get_value("Project", {"company": company} if company else {})
	if not name:
		frappe.throw(_("Purchase order approval needs a Project."))
	return name


def on_purchase_order(approval: dict, decision: str) -> str | None:
	if decision != APPROVED:
		return None
	name = approval.get("ref_name")
	if not name:
		return "Purchase order has no document."
	import frappe

	po = frappe.get_doc("Purchase Order", name)
	if po.docstatus == 1:
		return None
	frappe.flags.in_atlas_po = True
	try:
		po.submit()
	except Exception as e:
		return str(e)
	finally:
		frappe.flags.in_atlas_po = False
	return None
