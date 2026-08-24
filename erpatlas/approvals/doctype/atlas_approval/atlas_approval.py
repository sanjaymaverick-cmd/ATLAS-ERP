import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, now_datetime, nowdate

from erpatlas.approvals.queue import (
	PENDING,
	refuse_decide,
	refuse_raise,
	register_handler,
	run_handler,
)


def _ensure_handlers():
	from erpatlas.approvals.queue import HANDLERS

	if "Hold booking" not in HANDLERS:
		from erpatlas.property_inventory.hold_booking import on_hold_booking

		register_handler("Hold booking", on_hold_booking)
	if "Commission" not in HANDLERS:
		from erpatlas.booking.commission_handler import on_commission

		register_handler("Commission", on_commission)
	if "Vendor" not in HANDLERS:
		from erpatlas.commercial.vendor_handler import on_vendor

		register_handler("Vendor", on_vendor)
	if "Document export" not in HANDLERS:
		from erpatlas.documents.export_handler import on_document_export

		register_handler("Document export", on_document_export)
	if "Change" not in HANDLERS:
		from erpatlas.change_control.handler import on_change

		register_handler("Change", on_change)
	if "Payment" not in HANDLERS:
		from erpatlas.booking.payment_handler import on_payment

		register_handler("Payment", on_payment)
	if "Purchase order" not in HANDLERS:
		from erpatlas.commercial.po import on_purchase_order

		register_handler("Purchase order", on_purchase_order)


class AtlasApproval(Document):
	def validate(self):
		err = refuse_raise(kind=self.kind, waiting_on=self.waiting_on, amount=self.amount)
		if err:
			frappe.throw(_(err))
		if self.creation:
			self.aging_days = date_diff(nowdate(), self.creation)
		else:
			self.aging_days = 0
		if not self.is_new():
			before = self.get_doc_before_save()
			if before and before.status != PENDING and self.status != before.status:
				frappe.throw(_("This item is already decided."))

	def before_insert(self):
		self.status = PENDING
		self.aging_days = 0
		if not self.requested_by:
			self.requested_by = frappe.session.user


@frappe.whitelist()
def decide(name: str, decision: str):
	_ensure_handlers()
	doc = frappe.get_doc("Atlas Approval", name)
	roles = frappe.get_roles()
	md_bypass = bool(frappe.db.get_single_value("Atlas Settings", "md_bypass_four_eyes"))
	err = refuse_decide(
		status=doc.status,
		decision=decision,
		roles=roles,
		waiting_on=doc.waiting_on,
		md_bypass=md_bypass,
		kind=doc.kind,
		requested_by=doc.requested_by,
		actor=frappe.session.user,
	)
	if err:
		frappe.throw(_(err))
	payload = {
		"kind": doc.kind,
		"name": doc.name,
		"ref_doctype": doc.ref_doctype,
		"ref_name": doc.ref_name,
		"amount": doc.amount,
		"context": doc.context,
	}
	handler_err = run_handler(payload, decision)
	if handler_err:
		frappe.throw(_(handler_err))
	doc.status = decision
	doc.decided_by = frappe.session.user
	doc.decided_at = now_datetime()
	doc.save()
	return doc.as_dict()
