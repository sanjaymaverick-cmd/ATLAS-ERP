import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.handover.gates import SNAG_CLOSED, SNAG_OPEN
from erpatlas.property_inventory.lock import CHANNEL_ROLES


class AtlasSnag(Document):
	def validate(self):
		if self.unit:
			self.project = frappe.db.get_value("Atlas Unit", self.unit, "project")
		if not self.handover and self.unit:
			self.handover = frappe.db.get_value("Atlas Handover Case", {"unit": self.unit})

	def after_insert(self):
		from erpatlas.handover.adapter import refresh_snags_open

		refresh_snags_open(self.unit)

	def on_update(self):
		from erpatlas.handover.adapter import refresh_snags_open

		refresh_snags_open(self.unit)


@frappe.whitelist()
def close_snag(snag: str):
	if set(frappe.get_roles()) & CHANNEL_ROLES:
		frappe.throw(_("Channel seats cannot close snags."))
	doc = frappe.get_doc("Atlas Snag", snag)
	if doc.status == SNAG_CLOSED:
		return {"snag": doc.name, "status": SNAG_CLOSED}
	doc.status = SNAG_CLOSED
	doc.save()
	return {"snag": doc.name, "status": SNAG_CLOSED}


@frappe.whitelist()
def raise_snag(unit: str, title: str):
	if set(frappe.get_roles()) & CHANNEL_ROLES:
		frappe.throw(_("Channel seats cannot raise snags."))
	doc = frappe.get_doc(
		{"doctype": "Atlas Snag", "unit": unit, "title": title, "status": SNAG_OPEN}
	)
	doc.insert()
	return doc.as_dict()
