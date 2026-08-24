"""Daily KPI snapshot. Read-only store of Command JSON. Never writes Unit, PE, or Approval."""

from __future__ import annotations

import json

import frappe
from frappe.utils import date_diff, today

from erpatlas.command.portfolio import heat_map


def capture_snapshot(as_of: str | None = None) -> str | None:
	day = as_of or today()
	if frappe.db.exists("Atlas KPI Snapshot", {"as_of": day}):
		return frappe.db.get_value("Atlas KPI Snapshot", {"as_of": day}, "name")
	from erpatlas.command.board import get_command

	payload = get_command()
	payload["as_of"] = day
	doc = frappe.get_doc(
		{"doctype": "Atlas KPI Snapshot", "as_of": day, "payload": json.dumps(payload, default=str)}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def sparkline_booking_value(days: int = 7) -> list:
	if not frappe.db.exists("DocType", "Atlas KPI Snapshot"):
		return []
	rows = frappe.get_all(
		"Atlas KPI Snapshot",
		fields=["as_of", "payload"],
		order_by="as_of desc",
		limit=days,
	)
	out = []
	for row in reversed(rows):
		try:
			body = json.loads(row.payload or "{}")
		except json.JSONDecodeError:
			body = {}
		out.append((body.get("money") or {}).get("booking_value_live") or 0)
	return out


def _portfolio_facts() -> list[dict]:
	projects = frappe.get_all("Project", fields=["name"])
	rows = []
	for p in projects:
		name = p.name
		open_ncrs = 0
		if frappe.db.exists("DocType", "Atlas Change Item"):
			open_ncrs = frappe.db.count(
				"Atlas Change Item",
				{"project": name, "kind": "ncr", "status": ["not in", ["closed", "rejected"]]},
			)
		pending = frappe.db.count("Atlas Approval", {"project": name, "status": "Pending"})
		gap = None
		if frappe.db.exists("DocType", "Atlas Site Diary"):
			last = frappe.db.get_value(
				"Atlas Site Diary",
				{"project": name},
				"diary_date",
				order_by="diary_date desc",
			)
			if last:
				gap = date_diff(today(), last)
			else:
				gap = 99
		rows.append(
			{
				"project": name,
				"open_ncrs": open_ncrs,
				"pending_approvals": pending,
				"diary_gap_days": gap,
			}
		)
	return heat_map(rows)


def recent_sparklines():
	from erpatlas.command.portfolio import sparkline

	return sparkline(sparkline_booking_value())
