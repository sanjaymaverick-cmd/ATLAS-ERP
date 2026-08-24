"""Land adapter. Rules live in land.gates. Never posts to Tally or creates a Payment Entry."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import today

from erpatlas.land.gates import (
	ACQUIRED,
	pack_titles_to_add,
	refuse_acquire,
	refuse_add_diligence,
	refuse_set_diligence,
	refuse_start_pack,
	status_on_diligence,
)


def _items(parcel: str) -> list[dict]:
	return frappe.get_all(
		"Atlas Diligence Item",
		filters={"parcel": parcel},
		fields=["name", "title", "status"],
	)


def _set_parcel_status(doc, status: str):
	doc.status = status
	frappe.flags.in_atlas_land = True
	try:
		doc.save()
	finally:
		frappe.flags.in_atlas_land = False


def on_diligence_added(parcel_name: str):
	doc = frappe.get_doc("Atlas Parcel", parcel_name)
	nxt = status_on_diligence(doc.status)
	if nxt != doc.status:
		_set_parcel_status(doc, nxt)


def start_title_pack(parcel_name: str) -> dict:
	doc = frappe.get_doc("Atlas Parcel", parcel_name)
	existing = [row.title for row in _items(parcel_name)]
	err = refuse_start_pack(parcel_status=doc.status, existing_titles=existing)
	if err:
		frappe.throw(_(err))
	added = []
	for title in pack_titles_to_add(existing):
		item = frappe.get_doc(
			{
				"doctype": "Atlas Diligence Item",
				"parcel": doc.name,
				"project": doc.project,
				"title": title,
				"status": "open",
			}
		)
		item.insert()
		added.append(item.name)
	on_diligence_added(doc.name)
	return {
		"parcel": doc.name,
		"added": added,
		"status": frappe.db.get_value("Atlas Parcel", doc.name, "status"),
	}


def set_diligence(item_name: str, status: str) -> dict:
	err = refuse_set_diligence(status=status)
	if err:
		frappe.throw(_(err))
	item = frappe.get_doc("Atlas Diligence Item", item_name)
	item.status = status
	item.save()
	return {"item": item.name, "status": item.status, "auto_action": False}


def add_diligence(parcel_name: str, title: str) -> dict:
	doc = frappe.get_doc("Atlas Parcel", parcel_name)
	err = refuse_add_diligence(title=title, parcel_status=doc.status)
	if err:
		frappe.throw(_(err))
	item = frappe.get_doc(
		{
			"doctype": "Atlas Diligence Item",
			"parcel": doc.name,
			"project": doc.project,
			"title": str(title or "").strip(),
			"status": "open",
		}
	)
	item.insert()
	return {"item": item.name, "status": item.status, "title": item.title}


def acquire_parcel(
	parcel_name: str,
	consideration=None,
	sale_deed_no: str | None = None,
	advocate_name: str | None = None,
) -> dict:
	doc = frappe.get_doc("Atlas Parcel", parcel_name)
	consideration = consideration if consideration not in (None, "") else doc.consideration
	sale_deed_no = sale_deed_no if sale_deed_no not in (None, "") else doc.sale_deed_no
	err = refuse_acquire(
		parcel_status=doc.status,
		items=_items(parcel_name),
		consideration=consideration,
		sale_deed_no=sale_deed_no,
	)
	if err:
		frappe.throw(_(err))
	doc.consideration = consideration
	doc.sale_deed_no = str(sale_deed_no).strip()
	if not doc.sale_deed_date:
		doc.sale_deed_date = today()
	if advocate_name:
		doc.advocate_name = advocate_name
	_set_parcel_status(doc, ACQUIRED)
	return {
		"parcel": doc.name,
		"status": ACQUIRED,
		"creates_payment_entry": False,
		"writes_unit": False,
	}
