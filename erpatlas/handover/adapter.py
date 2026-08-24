"""Handover adapter. Writes via lock_adapter. Rules live in handover.gates."""

from __future__ import annotations

import frappe
from frappe import _

from erpatlas.booking.plan import POSSESSION, booking_live_unit
from erpatlas.handover.gates import (
	HANDOVER_POSSESSION,
	HANDOVER_SNAGGING,
	OC_RECEIVED,
	SNAG_OPEN,
	open_snag_count,
	possession_effects,
	refuse_possession,
)
from erpatlas.property_inventory.lock import BOOKED, CHANNEL_ROLES, SOLD


def ensure_handover(booking) -> str:
	existing = frappe.db.exists("Atlas Handover Case", {"booking": booking.name})
	if existing:
		return existing
	doc = frappe.get_doc(
		{
			"doctype": "Atlas Handover Case",
			"booking": booking.name,
			"unit": booking.unit,
			"project": booking.project,
			"channel_company": booking.channel_company,
			"occupancy_certificate": "Pending",
			"snags_open": 0,
			"status": HANDOVER_SNAGGING,
		}
	)
	frappe.flags.in_atlas_handover = True
	try:
		doc.insert(ignore_permissions=True)
	finally:
		frappe.flags.in_atlas_handover = False
	return doc.name


def refresh_snags_open(unit: str):
	n = frappe.db.count("Atlas Snag", {"unit": unit, "status": SNAG_OPEN})
	for name in frappe.get_all("Atlas Handover Case", filters={"unit": unit}, pluck="name"):
		frappe.db.set_value("Atlas Handover Case", name, "snags_open", n)


def receive_occupancy_certificate(handover_name: str) -> dict:
	_refuse_channel()
	doc = frappe.get_doc("Atlas Handover Case", handover_name)
	doc.occupancy_certificate = OC_RECEIVED
	frappe.flags.in_atlas_handover = True
	try:
		doc.save()
	finally:
		frappe.flags.in_atlas_handover = False
	return {"handover": doc.name, "occupancy_certificate": OC_RECEIVED}


def grant_possession(handover_name: str) -> dict:
	_refuse_channel()
	case = frappe.get_doc("Atlas Handover Case", handover_name)
	booking = frappe.get_doc("Atlas Booking", case.booking)
	unit_status = frappe.db.get_value("Atlas Unit", case.unit, "status")
	plan_gross = 0
	plan_collected = 0
	for row in booking.payment_steps:
		plan_gross += float(row.gross or 0)
		plan_collected += float(row.collected or 0)
	if not booking.payment_steps:
		plan_gross = float(booking.total_consideration or 0)
		plan_collected = float(booking.collected or 0)
	open_n = frappe.db.count("Atlas Snag", {"unit": case.unit, "status": SNAG_OPEN})
	err = refuse_possession(
		occupancy_certificate=case.occupancy_certificate,
		open_snags=open_n,
		plan_collected=plan_collected,
		plan_gross=plan_gross,
		booking_status=booking.status,
		unit_status=unit_status,
	)
	if err:
		frappe.throw(_(err))
	from erpatlas.property_inventory.lock_adapter import try_set_status

	moved = try_set_status(case.unit, BOOKED, SOLD, f"Possession {booking.name}")
	if moved:
		frappe.throw(_(moved))
	effects = possession_effects()
	booking.status = effects["booking_to"]
	booking.live_unit = booking_live_unit(
		status=POSSESSION, unit=booking.unit, booking_name=booking.name
	)
	frappe.flags.in_atlas_booking = True
	try:
		booking.save(ignore_permissions=True)
	finally:
		frappe.flags.in_atlas_booking = False
	case.status = HANDOVER_POSSESSION
	case.snags_open = 0
	frappe.flags.in_atlas_handover = True
	try:
		case.save(ignore_permissions=True)
	finally:
		frappe.flags.in_atlas_handover = False
	return {
		"handover": case.name,
		"booking": booking.name,
		"unit_status": SOLD,
		"booking_status": POSSESSION,
	}


def _refuse_channel():
	if set(frappe.get_roles()) & CHANNEL_ROLES:
		frappe.throw(_("Channel seats cannot grant possession or record Occupancy Certificate."))
