"""Daily report adapter. Wired as atlas_has_today_report."""

from __future__ import annotations


def has_today_report() -> bool:
	import frappe
	from frappe.utils import today

	from erpatlas.property_inventory.lock import CHANNEL_ROLES
	from erpatlas.property_inventory.permissions import channel_company_for

	if not set(frappe.get_roles()) & CHANNEL_ROLES:
		return True
	agent = frappe.session.user
	return bool(
		frappe.db.exists(
			"Atlas Daily Report",
			{"agent": agent, "report_date": today()},
		)
	)


def bind_channel_company(doc):
	import frappe
	from frappe import _

	from erpatlas.property_inventory.lock import CHANNEL_ROLES
	from erpatlas.property_inventory.permissions import channel_company_for

	if set(frappe.get_roles()) & CHANNEL_ROLES:
		company = channel_company_for(frappe.session.user)
		if not company:
			frappe.throw(_("Channel seats must be bound to a Channel Company."))
		doc.channel_company = company
	if not doc.agent:
		doc.agent = frappe.session.user
