from __future__ import annotations

from erpatlas.property_inventory.permissions import (
	_roles,
	channel_company_for,
	is_channel,
)


def lead_query_clause(company_sql: str | None) -> str:
	if not company_sql:
		return "1=0"
	return f"`tabLead`.atlas_channel_company = {company_sql}"


def lead_query(user):
	import frappe

	roles = _roles(user)
	if "System Manager" in roles or "Atlas Developer Admin" in roles:
		return ""
	if not is_channel(user):
		return ""
	company = channel_company_for(user)
	if not company:
		return lead_query_clause(None)
	return lead_query_clause(frappe.db.escape(company))


def has_lead_permission(doc, user=None, permission_type="read"):
	import frappe

	user = user or frappe.session.user
	if not is_channel(user):
		return True
	company = channel_company_for(user)
	return bool(company) and doc.get("atlas_channel_company") == company
