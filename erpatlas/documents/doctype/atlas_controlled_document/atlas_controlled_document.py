import frappe
from frappe.model.document import Document


class AtlasControlledDocument(Document):
	def before_insert(self):
		if not self.status:
			self.status = "Quarantine"


@frappe.whitelist()
def request_export(document: str):
	from erpatlas.documents.adapter import request_export as request

	return request(document)


@frappe.whitelist()
def clear_quarantine(document: str):
	from erpatlas.documents.adapter import clear_quarantine as clear

	return clear(document)


@frappe.whitelist()
def issue(document: str):
	from erpatlas.documents.adapter import issue_document

	return issue_document(document)
