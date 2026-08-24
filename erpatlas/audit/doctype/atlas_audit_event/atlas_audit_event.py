import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

from erpatlas.audit.log import refuse_edit


class AtlasAuditEvent(Document):
	def validate(self):
		if not self.is_new():
			frappe.throw(_(refuse_edit()))
		if not self.at:
			self.at = now_datetime()
		if not self.actor:
			self.actor = frappe.session.user


def record(action: str, entity: str, ref: str | None = None) -> str:
	doc = frappe.get_doc(
		{
			"doctype": "Atlas Audit Event",
			"at": now_datetime(),
			"actor": frappe.session.user,
			"action": action,
			"entity": entity,
			"ref": ref,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name
