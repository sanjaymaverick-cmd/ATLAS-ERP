"""Mixin on ERPNext Sales Order. Native Selling without a booking stays unlocked."""


class AtlasSalesOrderMixin:
	def validate(self):
		super().validate()
		if not self.get("atlas_booking"):
			return
		import frappe

		if not self.get("atlas_unit"):
			frappe.throw("An Atlas Booking Sales Order needs an Atlas Unit.")
		other = frappe.db.exists(
			"Sales Order",
			{
				"atlas_booking": self.atlas_booking,
				"name": ["!=", self.name or ""],
				"docstatus": ["in", [0, 1]],
			},
		)
		if other:
			frappe.throw("One live Sales Order per Atlas Booking.")
