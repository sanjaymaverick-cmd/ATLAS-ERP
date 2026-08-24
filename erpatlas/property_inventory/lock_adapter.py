"""MariaDB compare-and-swap for Atlas Unit status. The only place that writes status."""

from __future__ import annotations

from erpatlas.property_inventory.lock import (
	HELD,
	HOLD_EXPIRED,
	holds_due_to_expire,
	live_unit_key,
	refuse_transition,
	unit_status_on_hold_expire,
)


def cas_status(unit_name: str, frm: str, to: str) -> bool:
	import frappe
	from frappe.utils import now_datetime

	row = frappe.db.sql(
		"select status from `tabAtlas Unit` where name = %s for update",
		unit_name,
	)
	if not row or row[0][0] != frm:
		return False
	frappe.db.sql(
		"""
		update `tabAtlas Unit`
		set status = %s, modified = %s
		where name = %s and status = %s
		""",
		(to, now_datetime(), unit_name, frm),
	)
	return frappe.db.get_value("Atlas Unit", unit_name, "status") == to


def try_set_status(unit_name: str, frm: str, to: str, note: str) -> str | None:
	import frappe
	from frappe.utils import now_datetime

	err = refuse_transition(frm, to)
	if err:
		return err
	if not cas_status(unit_name, frm, to):
		current = frappe.db.get_value("Atlas Unit", unit_name, ["status", "code"], as_dict=True)
		if not current:
			return "Unit not found."
		return f"Unit {current.code} is {current.status} — {to.lower()} refused."
	frappe.flags.in_atlas_lock = True
	try:
		doc = frappe.get_doc("Atlas Unit", unit_name)
		doc.append(
			"events",
			{
				"at": now_datetime(),
				"from_status": frm,
				"to_status": to,
				"note": note,
				"actor": frappe.session.user,
			},
		)
		doc.save(ignore_permissions=True)
	finally:
		frappe.flags.in_atlas_lock = False
	return None


def expire_due_holds() -> int:
	import frappe
	from frappe.utils import today

	rows = frappe.get_all(
		"Atlas Unit Hold",
		filters={"status": HELD},
		fields=["name", "unit", "until", "status"],
	)
	due = holds_due_to_expire(rows, today())
	n = 0
	for hold in due:
		unit_status = frappe.db.get_value("Atlas Unit", hold["unit"], "status")
		target = unit_status_on_hold_expire(unit_status or "")
		if target:
			err = try_set_status(hold["unit"], unit_status, target, "Hold expired")
			if err:
				continue
		doc = frappe.get_doc("Atlas Unit Hold", hold["name"])
		doc.status = HOLD_EXPIRED
		doc.live_unit = live_unit_key(status=HOLD_EXPIRED, unit=doc.unit, hold_name=doc.name)
		doc.save(ignore_permissions=True)
		n += 1
	return n
