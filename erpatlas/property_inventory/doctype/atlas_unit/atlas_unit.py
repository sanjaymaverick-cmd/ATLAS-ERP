import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.property_inventory.lock import DISPUTE, refuse_dispute, refuse_transition


class AtlasUnit(Document):
	def validate(self):
		self.project_code_key = f"{self.project}::{self.code}"
		self._validate_tower_project()
		self._lock_status()

	def _validate_tower_project(self):
		if not self.tower:
			return
		tower_project = frappe.db.get_value("Atlas Tower", self.tower, "project")
		if tower_project and tower_project != self.project:
			frappe.throw(_("Tower {0} does not belong to this project.").format(self.tower))

	def _lock_status(self):
		if self.is_new():
			if not self.status:
				self.status = "Available"
			return
		if frappe.flags.get("in_atlas_lock"):
			return
		before = self.get_doc_before_save()
		if not before or before.status == self.status:
			return
		if self.status == DISPUTE:
			err = refuse_dispute(
				status=before.status,
				code=self.code,
				roles=frappe.get_roles(),
			)
			if err:
				frappe.throw(_(err))
			err = refuse_transition(before.status, self.status)
			if err:
				frappe.throw(_(err))
			self.append(
				"events",
				{
					"at": frappe.utils.now_datetime(),
					"from_status": before.status,
					"to_status": self.status,
					"note": "Marked dispute",
					"actor": frappe.session.user,
				},
			)
			return
		frappe.throw(_("Unit status is locked. Use Hold, Booking, Release, or Possession."))


@frappe.whitelist()
def mark_dispute(unit: str):
	doc = frappe.get_doc("Atlas Unit", unit)
	err = refuse_dispute(status=doc.status, code=doc.code, roles=frappe.get_roles())
	if err:
		frappe.throw(_(err))
	from erpatlas.property_inventory.lock_adapter import try_set_status

	moved = try_set_status(doc.name, doc.status, DISPUTE, "Marked dispute")
	if moved:
		frappe.throw(_(moved))
	return {"status": DISPUTE}
