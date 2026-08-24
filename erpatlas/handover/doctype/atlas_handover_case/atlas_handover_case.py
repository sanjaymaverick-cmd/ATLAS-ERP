import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.handover.gates import HANDOVER_SNAGGING


class AtlasHandoverCase(Document):
	def validate(self):
		if self.booking:
			booking = frappe.get_doc("Atlas Booking", self.booking)
			self.unit = booking.unit
			self.project = booking.project
			self.channel_company = booking.channel_company
		if self.is_new():
			if not self.status:
				self.status = HANDOVER_SNAGGING
			return
		if frappe.flags.get("in_atlas_handover"):
			return
		before = self.get_doc_before_save()
		if before and before.status != self.status:
			frappe.throw(_("Handover status is locked. Use Occupancy Certificate or Grant possession."))


@frappe.whitelist()
def receive_occupancy_certificate(handover: str):
	from erpatlas.handover.adapter import receive_occupancy_certificate as receive

	return receive(handover)


@frappe.whitelist()
def grant_possession(handover: str):
	from erpatlas.handover.adapter import grant_possession as grant

	return grant(handover)
