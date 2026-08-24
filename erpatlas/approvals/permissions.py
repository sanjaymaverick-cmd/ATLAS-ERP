from __future__ import annotations


def approval_query(user):
	"""Channel seats do not see the decision queue."""
	import frappe

	roles = set(frappe.get_roles(user))
	if "System Manager" in roles or "Atlas Developer Admin" in roles:
		return ""
	if roles & {"Atlas Channel Agent", "Atlas Channel Admin"}:
		return "1=0"
	return ""
