import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.controls.quantity import (
	APPROVED,
	derived_status,
	refuse_approve,
	refuse_edit_locked,
	refuse_qty,
	variance_qty,
)


class AtlasQuantity(Document):
	def validate(self):
		err = refuse_qty(qty=self.drawing_qty)
		if err:
			frappe.throw(_(err))
		err = refuse_qty(qty=self.site_qty)
		if err:
			frappe.throw(_(err))
		if frappe.flags.get("in_atlas_quantity"):
			self.variance = float(variance_qty(drawing_qty=self.drawing_qty, site_qty=self.site_qty))
			return
		if not self.is_new():
			before = self.get_doc_before_save()
			if before:
				locked = refuse_edit_locked(status=before.status)
				if locked and (
					before.drawing_qty != self.drawing_qty
					or before.site_qty != self.site_qty
					or before.status != self.status
				):
					frappe.throw(_(locked))
				if before.status != self.status:
					frappe.throw(_("Quantity status is locked. Use Approve quantity."))
		self.variance = float(variance_qty(drawing_qty=self.drawing_qty, site_qty=self.site_qty))
		self.status = derived_status(
			drawing_qty=self.drawing_qty, site_qty=self.site_qty, status=self.status
		)


@frappe.whitelist()
def approve(quantity: str):
	doc = frappe.get_doc("Atlas Quantity", quantity)
	err = refuse_approve(status=doc.status)
	if err:
		frappe.throw(_(err))
	doc.status = APPROVED
	frappe.flags.in_atlas_quantity = True
	try:
		doc.save()
	finally:
		frappe.flags.in_atlas_quantity = False
	return {
		"quantity": doc.name,
		"status": APPROVED,
		"creates_payment_entry": False,
		"writes_unit": False,
	}
