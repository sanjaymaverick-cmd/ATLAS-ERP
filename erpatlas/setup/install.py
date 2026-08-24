from __future__ import annotations

ATLAS_ROLES = [
	"Atlas Developer Admin",
	"Atlas Project Director",
	"Atlas Sales Manager",
	"Atlas Channel Admin",
	"Atlas Channel Agent",
	"Atlas Commercial",
	"Atlas Finance",
	"Atlas Site",
	"Atlas Stores",
	"Atlas Land Legal",
	"Atlas Documents",
]


def after_install():
	import frappe

	for role in ATLAS_ROLES:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(
				ignore_permissions=True
			)
	if not frappe.db.exists("Atlas Settings"):
		frappe.get_doc({"doctype": "Atlas Settings", "md_bypass_four_eyes": 1, "default_hold_days": 7}).insert(
			ignore_permissions=True
		)
	from erpatlas.setup.custom_fields import ensure_custom_fields

	ensure_custom_fields()
	_add_developer_admin_to_administrator()


def _add_developer_admin_to_administrator():
	import frappe

	user = frappe.get_doc("User", "Administrator")
	if not any(r.role == "Atlas Developer Admin" for r in user.roles):
		user.append("roles", {"role": "Atlas Developer Admin"})
		user.save(ignore_permissions=True)
