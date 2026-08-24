import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.change_control.flow import (
	refuse_close_ncr,
	refuse_respond,
	status_after_respond,
	vo_needs_amount,
)


class AtlasChangeItem(Document):
	def validate(self):
		err = vo_needs_amount(self.kind, self.amount)
		if err and self.kind == "change" and self.status in ("review", "approved"):
			frappe.throw(_(err))


@frappe.whitelist()
def close_ncr(name: str):
	doc = frappe.get_doc("Atlas Change Item", name)
	result = None
	if doc.reinspection:
		result = frappe.db.get_value("Atlas Inspection", doc.reinspection, "result")
	err = refuse_close_ncr(kind=doc.kind, status=doc.status, reinspection_result=result)
	if err:
		frappe.throw(_(err))
	doc.status = "closed"
	doc.save()
	return {"status": "closed"}


@frappe.whitelist()
def respond(name: str, response: str):
	doc = frappe.get_doc("Atlas Change Item", name)
	err = refuse_respond(kind=doc.kind, response=response, status=doc.status)
	if err:
		frappe.throw(_(err))
	doc.response = response
	doc.status = status_after_respond(doc.kind)
	doc.save()
	return {"status": doc.status, "creates_payment_entry": False}


@frappe.whitelist()
def send_vo_for_approval(name: str):
	doc = frappe.get_doc("Atlas Change Item", name)
	err = vo_needs_amount(doc.kind, doc.amount)
	if err:
		frappe.throw(_(err))
	from erpatlas.approvals.intake import raise_approval

	approval = raise_approval(
		kind="Change",
		title=doc.title,
		project=doc.project,
		waiting_on="Project Director",
		amount=float(doc.amount) if doc.amount else None,
		ref_doctype="Atlas Change Item",
		ref_name=doc.name,
		context="Variation. Not a Payment Entry.",
	)
	doc.status = "review"
	doc.save()
	return {"approval": approval}
