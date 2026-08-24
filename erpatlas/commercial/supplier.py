"""Mixin on ERPNext Supplier. GSTIN required to become Active."""


class AtlasSupplierMixin:
	def validate(self):
		super().validate()
		if self.get("atlas_stage") != "Active":
			return
		from erpatlas.commercial.vendor import refuse_vendor_active
		import frappe

		err = refuse_vendor_active(gstin=self.get("gstin") or self.get("tax_id"))
		if err:
			frappe.throw(err)
