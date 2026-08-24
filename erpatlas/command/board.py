"""Thin Command adapter. Reads live DocTypes. Never writes Unit, PE, or Approval."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import today

from erpatlas.command.kpis import (
	DEFAULT_APPROVAL_SLA_DAYS,
	DEFAULT_HOLD_EXPIRING_DAYS,
	build_command,
	refuse_command_access,
)


def projects_for_legal_entity(company: str | None) -> set[str] | None:
	"""Legal Entity = ERPNext Company. Inventory is keyed by Project."""
	if not company:
		return None
	names = frappe.get_all("Project", filters={"company": company}, pluck="name")
	return set(names)


def resolve_project_names(*, company: str | None, project: str | None) -> set[str] | None:
	if project:
		if company:
			project_company = frappe.db.get_value("Project", project, "company")
			if project_company and project_company != company:
				frappe.throw(_("That project does not belong to this Legal Entity."))
		return {project}
	return projects_for_legal_entity(company)


@frappe.whitelist()
def get_command(company: str | None = None, project: str | None = None) -> dict:
	err = refuse_command_access(frappe.get_roles())
	if err:
		frappe.throw(_(err))
	company = company or None
	project = project or None
	project_names = resolve_project_names(company=company, project=project)
	if company and project_names is not None and not project_names:
		empty = build_command(units=[], holds=[], approvals=[], today=today())
		empty["filters"] = {"company": company, "project": project}
		return empty

	unit_filters: dict = {}
	hold_filters: dict = {}
	approval_filters: dict = {"status": "Pending"}
	if project_names is not None:
		names = list(project_names)
		unit_filters["project"] = ["in", names]
		hold_filters["project"] = ["in", names]
		approval_filters["project"] = ["in", names]

	units = frappe.get_all("Atlas Unit", filters=unit_filters, fields=["name", "status", "project"])
	holds = frappe.get_all(
		"Atlas Unit Hold",
		filters=hold_filters,
		fields=["name", "status", "until", "project", "customer_name"],
	)
	approvals = frappe.get_all(
		"Atlas Approval",
		filters=approval_filters,
		fields=[
			"name",
			"title",
			"kind",
			"waiting_on",
			"aging_days",
			"amount",
			"project",
			"status",
			"creation",
			"context",
		],
		order_by="aging_days desc",
	)
	payload = build_command(
		units=units,
		holds=holds,
		approvals=approvals,
		today=today(),
		project_names=None,
		sla_days=DEFAULT_APPROVAL_SLA_DAYS,
		hold_expiring_days=DEFAULT_HOLD_EXPIRING_DAYS,
	)
	payload["filters"] = {"company": company, "project": project}
	return payload
