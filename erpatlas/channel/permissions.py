from __future__ import annotations

from erpatlas.property_inventory.permissions import (
	_roles,
	channel_company_for,
	is_channel,
)


def daily_report_query(user):
	import frappe

	roles = _roles(user)
	if "System Manager" in roles or "Atlas Developer Admin" in roles:
		return ""
	if not is_channel(user):
		return ""
	company = channel_company_for(user)
	if not company:
		return "1=0"
	return f"`tabAtlas Daily Report`.channel_company = {frappe.db.escape(company)}"


def has_daily_report_permission(doc, user=None, permission_type="read"):
	import frappe

	user = user or frappe.session.user
	if not is_channel(user):
		return True
	company = channel_company_for(user)
	return bool(company) and doc.channel_company == company
