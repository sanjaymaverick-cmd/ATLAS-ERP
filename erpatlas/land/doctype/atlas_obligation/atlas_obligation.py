import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today

from erpatlas.land.gates import overdue, refuse_file


class AtlasObligation(Document):
	def validate(self):
		if self.status != "filed" and overdue(
			status=self.status or "open", due=str(self.due or ""), today=today()
		):
			self.status = "overdue"


@frappe.whitelist()
def mark_filed(name: str, filed_ref: str | None = None):
	doc = frappe.get_doc("Atlas Obligation", name)
	err = refuse_file(status=doc.status)
	if err:
		frappe.throw(_(err))
	doc.status = "filed"
	if filed_ref:
		doc.filed_ref = filed_ref
	doc.save()
	return {"status": "filed"}
