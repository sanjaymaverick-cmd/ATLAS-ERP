import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today

from erpatlas.site.gates import FAIL, PENDING, ncr_from_fail, refuse_complete


class AtlasInspection(Document):
	def before_insert(self):
		if not self.inspection_date:
			self.inspection_date = today()
		if not self.result:
			self.result = PENDING


@frappe.whitelist()
def complete(inspection: str, result: str):
	doc = frappe.get_doc("Atlas Inspection", inspection)
	err = refuse_complete(current=doc.result, result=result)
	if err:
		frappe.throw(_(err))
	doc.result = result
	if result == FAIL:
		facts = ncr_from_fail(template=doc.template, location=doc.location)
		ncr = frappe.get_doc(
			{
				"doctype": "Atlas Change Item",
				"project": doc.project,
				"kind": facts["kind"],
				"title": facts["title"],
				"status": facts["status"],
				"severity": "medium",
				"inspection": doc.name,
			}
		)
		ncr.insert(ignore_permissions=True)
		doc.ncr = ncr.name
	doc.save()
	return {"inspection": doc.name, "result": doc.result, "ncr": doc.ncr}
