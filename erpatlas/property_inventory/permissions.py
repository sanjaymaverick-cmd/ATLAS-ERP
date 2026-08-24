from __future__ import annotations

CHANNEL_ROLES = frozenset({"Atlas Channel Agent", "Atlas Channel Admin"})


def unit_query_clause(company_sql: str | None) -> str:
	"""SQL fragment. `company_sql` is already escaped (quotes included), or None."""
	available = "`tabAtlas Unit`.status = 'Available'"
	if not company_sql:
		return f"({available})"
	return f"""({available} or exists (
		select 1 from `tabAtlas Unit Hold` h
		where h.unit = `tabAtlas Unit`.name
			and h.channel_company = {company_sql}
	) or exists (
		select 1 from `tabAtlas Booking` b
		where b.unit = `tabAtlas Unit`.name
			and b.channel_company = {company_sql}
			and b.status in ('Active', 'Possession')
	))"""


def booking_query_clause(company_sql: str | None) -> str:
	if not company_sql:
		return "1=0"
	return f"`tabAtlas Booking`.channel_company = {company_sql}"


def commission_query_clause(company_sql: str | None) -> str:
	if not company_sql:
		return "1=0"
	return f"`tabAtlas Commission`.channel_company = {company_sql}"


def _roles(user):
	import frappe

	return set(frappe.get_roles(user))


def channel_company_for(user) -> str | None:
	import frappe

	perms = frappe.defaults.get_user_permissions(user) or {}
	rows = perms.get("Atlas Channel Company") or []
	if not rows:
		return None
	first = rows[0]
	if isinstance(first, dict):
		return first.get("doc") or first.get("name")
	return first


def is_channel(user) -> bool:
	return bool(_roles(user) & CHANNEL_ROLES)


def unit_query(user):
	import frappe

	roles = _roles(user)
	if "System Manager" in roles or "Atlas Developer Admin" in roles:
		return ""
	if not is_channel(user):
		return ""
	company = channel_company_for(user)
	if not company:
		return unit_query_clause(None)
	return unit_query_clause(frappe.db.escape(company))


def hold_query(user):
	import frappe

	roles = _roles(user)
	if "System Manager" in roles or "Atlas Developer Admin" in roles:
		return ""
	if not is_channel(user):
		return ""
	company = channel_company_for(user)
	if not company:
		return "1=0"
	return f"`tabAtlas Unit Hold`.channel_company = {frappe.db.escape(company)}"


def channel_company_query(user):
	import frappe

	roles = _roles(user)
	if "System Manager" in roles or "Atlas Developer Admin" in roles:
		return ""
	if not is_channel(user):
		return ""
	company = channel_company_for(user)
	if not company:
		return "1=0"
	return f"`tabAtlas Channel Company`.name = {frappe.db.escape(company)}"


def has_unit_permission(doc, user=None, permission_type="read"):
	import frappe

	user = user or frappe.session.user
	if not is_channel(user):
		return True
	from erpatlas.booking.plan import channel_may_read_unit

	company = channel_company_for(user)
	if not company:
		return channel_may_read_unit(status=doc.status, own_hold=False, own_booking=False)
	own_hold = bool(
		frappe.db.exists("Atlas Unit Hold", {"unit": doc.name, "channel_company": company})
	)
	own_booking = bool(
		frappe.db.exists(
			"Atlas Booking",
			{"unit": doc.name, "channel_company": company, "status": ["in", ["Active", "Possession"]]},
		)
	)
	return channel_may_read_unit(status=doc.status, own_hold=own_hold, own_booking=own_booking)


def has_hold_permission(doc, user=None, permission_type="read"):
	import frappe

	user = user or frappe.session.user
	if not is_channel(user):
		return True
	company = channel_company_for(user)
	return bool(company) and doc.channel_company == company


def has_channel_company_permission(doc, user=None, permission_type="read"):
	import frappe

	user = user or frappe.session.user
	if not is_channel(user):
		return True
	return doc.name == channel_company_for(user)
