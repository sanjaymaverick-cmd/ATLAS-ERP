import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.change_control.flow import refuse_close_ncr, vo_needs_amount


class AtlasChangeItem(Document):
	def validate(self):
		err = vo_needs_amount(self.kind, self.amount)
		if err and self.kind == "change" and self.status in ("review", "approved"):
			frappe.throw(_(err))


@frappe.whitelist()
def close_ncr(name: str):
	doc = frappe.get_doc("Atlas Change Item", name)
	err = refuse_close_ncr(kind=doc.kind, status=doc.status)
	if err:
		frappe.throw(_(err))
	doc.status = "closed"
	doc.save()
	return {"status": "closed"}


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
