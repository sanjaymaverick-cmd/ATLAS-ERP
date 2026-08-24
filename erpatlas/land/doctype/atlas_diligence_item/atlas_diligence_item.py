import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.land.gates import refuse_add_diligence, refuse_set_diligence


class AtlasDiligenceItem(Document):
	def validate(self):
		parcel_status = None
		if self.parcel:
			row = frappe.db.get_value("Atlas Parcel", self.parcel, ["project", "status"], as_dict=True)
			if row:
				self.project = row.project
				parcel_status = row.status
		if self.is_new():
			err = refuse_add_diligence(title=self.title, parcel_status=parcel_status)
			if err:
				frappe.throw(_(err))
			return
		err = refuse_set_diligence(status=self.status)
		if err:
			frappe.throw(_(err))

	def after_insert(self):
		from erpatlas.land.adapter import on_diligence_added

		on_diligence_added(self.parcel)


@frappe.whitelist()
def set_status(item: str, status: str):
	from erpatlas.land.adapter import set_diligence

	return set_diligence(item, status)
