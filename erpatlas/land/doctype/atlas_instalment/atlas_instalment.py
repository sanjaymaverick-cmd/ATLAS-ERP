import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.land.instalment import PAID, refuse_pay


class AtlasInstalment(Document):
	def validate(self):
		if self.parcel and not self.project:
			self.project = frappe.db.get_value("Atlas Parcel", self.parcel, "project")


@frappe.whitelist()
def mark_paid(name: str):
	doc = frappe.get_doc("Atlas Instalment", name)
	err = refuse_pay(status=doc.status, amount=doc.amount)
	if err:
		frappe.throw(_(err))
	doc.status = PAID
	doc.save()
	return {
		"status": PAID,
		"creates_payment_entry": False,
		"posts_to_tally": False,
	}
