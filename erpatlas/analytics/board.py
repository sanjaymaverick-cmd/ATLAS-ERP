"""Thin Sales Analytics adapter. Reads Lead scores. Never writes Unit, PE, or Approval."""

from __future__ import annotations

import frappe
from frappe import _

from erpatlas.analytics.funnel import build_sales_analytics
from erpatlas.command.kpis import refuse_command_access
from erpatlas.property_inventory.lock import CHANNEL_ROLES


@frappe.whitelist()
def get_sales_analytics(company: str | None = None, project: str | None = None) -> dict:
	roles = frappe.get_roles()
	role_set = set(roles)
	if "Administrator" not in role_set and role_set & CHANNEL_ROLES:
		frappe.throw(_("Channel seats cannot open Sales Analytics."))
	err = refuse_command_access(roles)
	if err:
		allowed = {"Atlas Developer Admin", "Atlas Project Director", "Atlas Sales Manager", "Atlas Finance"}
		if not role_set & allowed:
			frappe.throw(_(err))
	filters: dict = {}
	if project:
		filters["atlas_project"] = project
	elif company:
		names = frappe.get_all("Project", filters={"company": company}, pluck="name")
		if names:
			filters["atlas_project"] = ["in", names]
		else:
			return build_sales_analytics([])
	fields = ["name", "atlas_stage", "atlas_band", "atlas_score_model", "atlas_project"]
	if not frappe.get_meta("Lead").has_field("atlas_stage"):
		return build_sales_analytics([])
	leads = frappe.get_all("Lead", filters=filters, fields=fields)
	payload = build_sales_analytics(leads)
	payload["filters"] = {"company": company, "project": project}
	return payload
