import frappe
from frappe import _
from frappe.model.document import Document


class AtlasExportGrant(Document):
	def validate(self):
		if self.document and not self.project:
			self.project = frappe.db.get_value("Atlas Controlled Document", self.document, "project")
		if self.is_new():
			if not self.requested_by:
				self.requested_by = frappe.session.user
			return
		if frappe.flags.get("in_atlas_grant"):
			return
		before = self.get_doc_before_save()
		if before and before.status != self.status:
			frappe.throw(_("Grant status is locked. Use Approvals or Consume."))


@frappe.whitelist()
def consume(grant: str):
	from erpatlas.documents.adapter import consume_export

	return consume_export(grant)
