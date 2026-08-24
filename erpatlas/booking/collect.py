"""Collect against the next unpaid Atlas Booking step. Never from Approvals."""

from __future__ import annotations

from erpatlas.booking.plan import refuse_cancel, refuse_collect_booking, next_collect_step
from erpatlas.books.payment_gst import money
from erpatlas.books.posting import collect_posting
from erpatlas.property_inventory.lock import AVAILABLE, BOOKED, CHANNEL_ROLES


def collect(booking_name: str, amount, *, mode_of_payment: str | None = None) -> dict:
	import frappe
	from frappe import _

	_refuse_channel_collector()
	booking = frappe.get_doc("Atlas Booking", booking_name)
	if not booking.sales_order:
		frappe.throw(_("Booking has no Sales Order."))
	steps = []
	for i, row in enumerate(booking.payment_steps):
		steps.append(
			{
				"idx": i,
				"gross": row.gross,
				"collected": row.collected or 0,
			}
		)
	step = next_collect_step(steps)
	plan_gross = money(0)
	plan_collected = money(booking.collected or 0)
	for row in booking.payment_steps:
		plan_gross += money(row.gross or 0)
	err = refuse_collect_booking(
		status=booking.status,
		step=step,
		receipt=amount,
		plan_collected=plan_collected,
		plan_gross=plan_gross,
	)
	if err:
		frappe.throw(_(err))
	posting = collect_posting(
		policy=booking.gst_policy or "on_receipt",
		receipt=amount,
		grand_total=plan_gross,
		sales_order=booking.sales_order,
	)
	si_name = None
	if posting["against"] == "Sales Invoice":
		si_name = _submit_step_invoice(booking, posting["invoice_qty"])
		against_dt, against_name = "Sales Invoice", si_name
	else:
		against_dt, against_name = "Sales Order", booking.sales_order
	pe_name = _submit_payment(
		booking,
		amount=amount,
		against_dt=against_dt,
		against_name=against_name,
		mode_of_payment=mode_of_payment,
	)
	idx = int(step["idx"])
	row = booking.payment_steps[idx]
	row.collected = float(money(row.collected or 0) + money(amount))
	row.payment_entry = pe_name
	if si_name:
		row.sales_invoice = si_name
	booking.collected = float(money(booking.collected or 0) + money(amount))
	frappe.flags.in_atlas_booking = True
	try:
		booking.save(ignore_permissions=True)
	finally:
		frappe.flags.in_atlas_booking = False
	return {
		"booking": booking.name,
		"sales_invoice": si_name,
		"payment_entry": pe_name,
		"collected": booking.collected,
	}


def cancel_booking(booking_name: str) -> dict:
	import frappe
	from frappe import _

	booking = frappe.get_doc("Atlas Booking", booking_name)
	unit_status = frappe.db.get_value("Atlas Unit", booking.unit, "status")
	has_money = bool(money(booking.collected or 0) > 0) or _has_posted_money(booking)
	err = refuse_cancel(
		status=booking.status, unit_status=unit_status, has_posted_money=has_money
	)
	if err:
		frappe.throw(_(err))
	if booking.sales_order:
		so = frappe.get_doc("Sales Order", booking.sales_order)
		if so.docstatus == 1:
			so.cancel()
	from erpatlas.property_inventory.lock_adapter import try_set_status

	moved = try_set_status(booking.unit, BOOKED, AVAILABLE, f"Booking {booking.name} cancelled")
	if moved:
		frappe.throw(_(moved))
	from erpatlas.booking.plan import CANCELLED, booking_live_unit

	booking.status = CANCELLED
	booking.live_unit = booking_live_unit(
		status=CANCELLED, unit=booking.unit, booking_name=booking.name
	)
	frappe.flags.in_atlas_booking = True
	try:
		booking.save(ignore_permissions=True)
	finally:
		frappe.flags.in_atlas_booking = False
	return {"booking": booking.name, "status": CANCELLED}


def _refuse_channel_collector():
	import frappe
	from frappe import _

	if set(frappe.get_roles()) & CHANNEL_ROLES:
		frappe.throw(_("Channel seats cannot collect. Finance or Sales posts the Payment Entry."))


def _has_posted_money(booking) -> bool:
	import frappe

	if frappe.db.exists("Sales Invoice", {"atlas_booking": booking.name, "docstatus": 1}):
		return True
	if frappe.db.exists("Payment Entry", {"atlas_booking": booking.name, "docstatus": 1}):
		return True
	return False


def _submit_step_invoice(booking, qty) -> str:
	import frappe
	from frappe import _

	try:
		from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
	except ImportError:
		frappe.throw(_("ERPNext Sales Invoice helper is not available on this site."))
	si = make_sales_invoice(booking.sales_order)
	for item in si.items:
		item.qty = float(qty)
	if hasattr(si, "atlas_booking"):
		si.atlas_booking = booking.name
	si.flags.ignore_permissions = True
	si.insert()
	si.submit()
	return si.name


def _submit_payment(booking, *, amount, against_dt, against_name, mode_of_payment):
	import frappe
	from frappe import _

	try:
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
	except ImportError:
		frappe.throw(_("ERPNext Payment Entry helper is not available on this site."))
	pe = get_payment_entry(against_dt, against_name, party_amount=float(money(amount)))
	pe.paid_amount = float(money(amount))
	pe.received_amount = float(money(amount))
	if mode_of_payment:
		pe.mode_of_payment = mode_of_payment
	if hasattr(pe, "atlas_booking"):
		pe.atlas_booking = booking.name
	pe.flags.ignore_permissions = True
	pe.insert()
	pe.submit()
	return pe.name
