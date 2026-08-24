import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.land.gates import IDENTIFIED, refuse_add_parcel


class AtlasParcel(Document):
	def validate(self):
		err = refuse_add_parcel(title=self.title, khasra=self.khasra)
		if err:
			frappe.throw(_(err))
		if self.is_new():
			if not self.status:
				self.status = IDENTIFIED
			return
		if frappe.flags.get("in_atlas_land"):
			return
		before = self.get_doc_before_save()
		if before and before.status != self.status:
			frappe.throw(_("Parcel status is locked. Use the title pack or Acquire."))


@frappe.whitelist()
def start_title_pack(parcel: str):
	from erpatlas.land.adapter import start_title_pack as start

	return start(parcel)


@frappe.whitelist()
def acquire(
	parcel: str,
	consideration=None,
	sale_deed_no: str | None = None,
	advocate_name: str | None = None,
):
	from erpatlas.land.adapter import acquire_parcel

	return acquire_parcel(parcel, consideration, sale_deed_no, advocate_name)


@frappe.whitelist()
def add_diligence(parcel: str, title: str):
	from erpatlas.land.adapter import add_diligence as add

	return add(parcel, title)
