import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.booking.plan import booking_live_unit, refuse_step_percents


class AtlasBooking(Document):
	def before_insert(self):
		if self.name:
			self.live_unit = booking_live_unit(
				status=self.status or "Draft", unit=self.unit, booking_name=self.name
			)

	def validate(self):
		unit = frappe.get_doc("Atlas Unit", self.unit)
		self.project = unit.project
		if not self.customer_name and self.customer:
			self.customer_name = frappe.db.get_value("Customer", self.customer, "customer_name")
		if self.payment_steps:
			err = refuse_step_percents(
				[{"percent": row.percent} for row in self.payment_steps]
			)
			if err:
				frappe.throw(_(err))
		if self.name:
			self.live_unit = booking_live_unit(
				status=self.status, unit=self.unit, booking_name=self.name
			)
		if self.is_new():
			return
		if frappe.flags.get("in_atlas_booking"):
			return
		before = self.get_doc_before_save()
		if before and before.status != self.status:
			frappe.throw(_("Booking status is locked. Use Activate, Collect, or Cancel."))

	def after_insert(self):
		key = booking_live_unit(status=self.status, unit=self.unit, booking_name=self.name)
		if key and self.live_unit != key:
			self.db_set("live_unit", key)


@frappe.whitelist()
def activate(booking: str):
	from erpatlas.booking.activate import activate_booking

	return activate_booking(booking)


@frappe.whitelist()
def collect(booking: str, amount: float, mode_of_payment: str | None = None):
	from erpatlas.booking.collect import collect as collect_against_plan

	return collect_against_plan(booking, amount, mode_of_payment=mode_of_payment)


@frappe.whitelist()
def cancel(booking: str):
	from erpatlas.booking.collect import cancel_booking

	return cancel_booking(booking)
