from __future__ import annotations

from erpatlas.property_inventory.permissions import (
	_roles,
	channel_company_for,
	is_channel,
)


def handover_query(user):
	import frappe

	roles = _roles(user)
	if "System Manager" in roles or "Atlas Developer Admin" in roles:
		return ""
	if not is_channel(user):
		return ""
	company = channel_company_for(user)
	if not company:
		return "1=0"
	return f"`tabAtlas Handover Case`.channel_company = {frappe.db.escape(company)}"


def snag_query(user):
	import frappe

	roles = _roles(user)
	if "System Manager" in roles or "Atlas Developer Admin" in roles:
		return ""
	if not is_channel(user):
		return ""
	company = channel_company_for(user)
	if not company:
		return "1=0"
	esc = frappe.db.escape(company)
	return f"""exists (
		select 1 from `tabAtlas Handover Case` h
		where h.name = `tabAtlas Snag`.handover
			and h.channel_company = {esc}
	)"""


def has_handover_permission(doc, user=None, permission_type="read"):
	import frappe

	user = user or frappe.session.user
	if not is_channel(user):
		return True
	company = channel_company_for(user)
	return bool(company) and doc.channel_company == company


def has_snag_permission(doc, user=None, permission_type="read"):
	import frappe

	user = user or frappe.session.user
	if not is_channel(user):
		return True
	if not doc.handover:
		return False
	company = channel_company_for(user)
	case_company = frappe.db.get_value("Atlas Handover Case", doc.handover, "channel_company")
	return bool(company) and case_company == company
