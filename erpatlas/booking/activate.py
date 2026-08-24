"""Activate an Atlas Booking: CAS unit → Booked, close Hold, submit Sales Order, accrue Commission.

frappe lives here. Rules live in booking.plan and books.payment_gst.
"""

from __future__ import annotations

from erpatlas.booking.plan import (
	ACTIVE,
	DRAFT,
	accrue_intent,
	activate_plan,
	booking_live_unit,
	default_steps,
	refuse_activate,
)
from erpatlas.books.payment_gst import INCLUSIVE, resolve_policy, resolve_rate
from erpatlas.property_inventory.lock import BOOKED, HELD, HOLD_BOOKED, HOLD_HELD, live_unit_key


def activate_from_hold(hold_name: str, *, consideration=None, steps=None, customer=None):
	import frappe
	from frappe import _

	hold = frappe.get_doc("Atlas Unit Hold", hold_name)
	if hold.status != HOLD_HELD:
		frappe.throw(_("Hold not active."))
	unit = frappe.get_doc("Atlas Unit", hold.unit)
	value = consideration if consideration not in (None, "") else hold.booking_value or unit.price
	customer_name = customer or hold.customer_name
	customer_id = ensure_customer(customer_name)
	step_rows = list(steps or default_steps())
	live = bool(
		frappe.db.exists(
			"Atlas Booking",
			{"unit": unit.name, "status": ["in", ["Active", "Possession"]]},
		)
	)
	err = refuse_activate(
		unit_status=unit.status,
		code=unit.code,
		live_booking=live,
		customer=customer_name,
		consideration=value,
		steps=step_rows,
		booking_status=DRAFT,
	)
	if err:
		frappe.throw(_(err))
	booking = frappe.get_doc(
		{
			"doctype": "Atlas Booking",
			"unit": unit.name,
			"project": unit.project,
			"hold": hold.name,
			"customer": customer_id,
			"customer_name": customer_name,
			"channel_company": hold.channel_company,
			"agent": hold.agent,
			"total_consideration": value,
			"status": DRAFT,
			"payment_steps": [
				{
					"label": row.get("label") or "Step",
					"kind": row.get("kind") or "slab",
					"percent": row["percent"],
					"due_date": row.get("due_date"),
				}
				for row in step_rows
			],
		}
	)
	booking.insert(ignore_permissions=True)
	return activate_booking(booking.name)


def activate_booking(booking_name: str) -> dict:
	import frappe
	from frappe import _

	booking = frappe.get_doc("Atlas Booking", booking_name)
	unit = frappe.get_doc("Atlas Unit", booking.unit)
	hold = frappe.get_doc("Atlas Unit Hold", booking.hold) if booking.hold else None
	if hold and hold.status != HOLD_HELD:
		frappe.throw(_("Hold not active."))
	step_rows = [
		{"label": s.label, "kind": s.kind, "percent": s.percent, "due_date": s.due_date}
		for s in booking.payment_steps
	] or default_steps()
	if not booking.payment_steps:
		for row in step_rows:
			booking.append("payment_steps", row)
	live = bool(
		frappe.db.exists(
			"Atlas Booking",
			{"unit": unit.name, "status": ["in", ["Active", "Possession"]], "name": ["!=", booking.name]},
		)
	)
	err = refuse_activate(
		unit_status=unit.status,
		code=unit.code,
		live_booking=live,
		customer=booking.customer or booking.customer_name,
		consideration=booking.total_consideration,
		steps=step_rows,
		booking_status=booking.status,
	)
	if err:
		frappe.throw(_(err))
	if not booking.customer:
		booking.customer = ensure_customer(booking.customer_name)

	facts = project_tax_facts(booking.project)
	try:
		policy = resolve_policy(
			oc_received=False,
			gst_on_under_construction=facts["gst_on_under_construction"],
			override=booking.gst_policy or None,
		)
		rate = resolve_rate(
			policy=policy,
			affordable=facts["affordable"],
			shop=unit.kind == "Shop",
			configured_rate=facts["gst_rate"],
		)
		tax_included = booking.tax_included or facts["tax_included"] or INCLUSIVE
		plan = activate_plan(
			consideration=booking.total_consideration,
			steps=step_rows,
			rate=rate,
			tax_included=tax_included,
		)
	except ValueError as e:
		frappe.throw(_(str(e)))

	from_status = HELD if hold else unit.status
	from erpatlas.property_inventory.lock_adapter import try_set_status

	moved = try_set_status(unit.name, from_status, BOOKED, f"Booking {booking.name}")
	if moved:
		frappe.throw(_(moved))

	if hold:
		hold.status = HOLD_BOOKED
		hold.booking_requested = 0
		hold.live_unit = live_unit_key(status=HOLD_BOOKED, unit=hold.unit, hold_name=hold.name)
		hold.save(ignore_permissions=True)

	for i, expanded in enumerate(plan["steps"]):
		row = booking.payment_steps[i]
		row.taxable = float(expanded["taxable"])
		row.gst = float(expanded["gst"])
		row.cgst = float(expanded["cgst"])
		row.sgst = float(expanded["sgst"])
		row.igst = float(expanded["igst"])
		row.gross = float(expanded["gross"])
		row.collected = 0

	booking.company = company_for_project(booking.project)
	booking.gst_policy = policy
	booking.gst_rate = float(rate)
	booking.tax_included = tax_included
	so = submit_sales_order(booking, plan, tax_template=facts["tax_template"])
	booking.sales_order = so
	intent = accrue_intent(
		channel_company=booking.channel_company,
		channel_status=_channel_status(booking.channel_company),
		rate=_channel_rate(booking.channel_company),
		consideration=booking.total_consideration,
		already_accrued=bool(booking.commission),
	)
	if intent:
		comm = frappe.get_doc(
			{
				"doctype": "Atlas Commission",
				"booking": booking.name,
				"channel_company": booking.channel_company,
				"project": booking.project,
				"amount": float(intent["amount"]),
				"status": intent["status"],
			}
		)
		frappe.flags.in_atlas_commission = True
		try:
			comm.insert(ignore_permissions=True)
		finally:
			frappe.flags.in_atlas_commission = False
		booking.commission = comm.name
	booking.status = ACTIVE
	booking.live_unit = booking_live_unit(
		status=ACTIVE, unit=booking.unit, booking_name=booking.name
	)
	frappe.flags.in_atlas_booking = True
	try:
		booking.save(ignore_permissions=True)
	finally:
		frappe.flags.in_atlas_booking = False
	return {"booking": booking.name, "sales_order": so, "commission": booking.commission}


def company_for_project(project: str) -> str:
	import frappe
	from frappe import _

	company = frappe.db.get_value("Project", project, "company")
	if not company:
		frappe.throw(_("Project has no Legal Entity (Company)."))
	return company


def project_tax_facts(project: str) -> dict:
	import frappe

	meta = frappe.get_meta("Project")
	fields = [
		name
		for name in (
			"gst_on_under_construction",
			"gst_rate",
			"atlas_tax_included",
			"atlas_affordable",
			"atlas_sales_tax_template",
		)
		if meta.has_field(name)
	]
	row = frappe.db.get_value("Project", project, fields, as_dict=True) if fields else {}
	row = row or {}
	gst_flag = row.get("gst_on_under_construction")
	if gst_flag is None:
		gst_flag = 1
	return {
		"gst_on_under_construction": bool(gst_flag),
		"gst_rate": row.get("gst_rate"),
		"tax_included": row.get("atlas_tax_included") or INCLUSIVE,
		"affordable": bool(row.get("atlas_affordable")),
		"tax_template": row.get("atlas_sales_tax_template"),
	}


def ensure_customer(name: str) -> str:
	import frappe

	existing = frappe.db.get_value("Customer", {"customer_name": name})
	if existing:
		return existing
	group = "All Customer Groups"
	for candidate in ("Individual", "All Customer Groups"):
		if frappe.db.exists("Customer Group", candidate):
			group = candidate
			break
	territory = "All Territories"
	if not frappe.db.exists("Territory", territory):
		any_t = frappe.db.get_value("Territory", {})
		territory = any_t or territory
	doc = frappe.get_doc(
		{
			"doctype": "Customer",
			"customer_name": name,
			"customer_type": "Individual",
			"customer_group": group,
			"territory": territory,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def ensure_unit_sale_item() -> str:
	import frappe

	code = "ATLAS-UNIT"
	if frappe.db.exists("Item", code):
		return code
	group = "All Item Groups"
	for candidate in ("Services", "Products", "All Item Groups"):
		if frappe.db.exists("Item Group", candidate):
			group = candidate
			break
	uom = "Nos" if frappe.db.exists("UOM", "Nos") else frappe.db.get_value("UOM", {})
	doc = frappe.get_doc(
		{
			"doctype": "Item",
			"item_code": code,
			"item_name": "Atlas Unit",
			"item_group": group,
			"stock_uom": uom or "Nos",
			"is_stock_item": 0,
			"is_sales_item": 1,
			"include_item_in_manufacturing": 0,
		}
	)
	doc.insert(ignore_permissions=True)
	return code


def submit_sales_order(booking, plan: dict, *, tax_template: str | None) -> str:
	import frappe
	from frappe.utils import today

	from erpatlas.books.posting import sales_order_payload

	payload = sales_order_payload(
		customer=booking.customer,
		company=booking.company,
		project=booking.project,
		item_code=ensure_unit_sale_item(),
		unit_code=frappe.db.get_value("Atlas Unit", booking.unit, "code") or booking.unit,
		booking=booking.name,
		unit=booking.unit,
		taxable_total=plan["taxable_total"],
		steps=plan["steps"],
		transaction_date=today(),
		delivery_date=today(),
	)
	if not tax_template:
		payload["items"][0]["rate"] = float(plan["grand_total"])
	so = frappe.get_doc(payload)
	if tax_template:
		so.taxes_and_charges = tax_template
	so.flags.ignore_permissions = True
	so.insert()
	so.submit()
	return so.name


def _channel_status(channel_company: str | None) -> str | None:
	import frappe

	if not channel_company:
		return None
	return frappe.db.get_value("Atlas Channel Company", channel_company, "status")


def _channel_rate(channel_company: str | None):
	import frappe

	if not channel_company:
		return None
	return frappe.db.get_value("Atlas Channel Company", channel_company, "rate")
