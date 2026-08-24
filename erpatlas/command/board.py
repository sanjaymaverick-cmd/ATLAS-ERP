"""Thin Command adapter. Reads live DocTypes. Never writes Unit, PE, or Approval."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import today

from erpatlas.command.kpis import build_command, refuse_command_access
from erpatlas.command.risk import DEFAULT_THRESHOLDS


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
	thresholds = command_thresholds()
	if company and project_names is not None and not project_names:
		empty = build_command(
			units=[],
			holds=[],
			approvals=[],
			today=today(),
			sla_days=int(thresholds["approval_sla_days"]),
			hold_expiring_days=int(thresholds["hold_expiring_days"]),
			thresholds=thresholds,
			cash_board=gl_cash_facts(company),
		)
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
		fields=["name", "status", "until", "project", "customer_name", "creation"],
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
	bookings, steps, payments, commissions = _booking_rows(project_names)
	handovers, snags = _handover_rows(project_names)
	vendors = _vendor_rows()
	payload = build_command(
		units=units,
		holds=holds,
		approvals=approvals,
		today=today(),
		project_names=None,
		sla_days=int(thresholds["approval_sla_days"]),
		hold_expiring_days=int(thresholds["hold_expiring_days"]),
		bookings=bookings,
		steps=steps,
		payments=payments,
		commissions=commissions,
		handovers=handovers,
		snags=snags,
		vendors=vendors,
		thresholds=thresholds,
		cash_board=gl_cash_facts(company),
	)
	payload["filters"] = {"company": company, "project": project}
	from erpatlas.command.snapshot import _portfolio_facts, sparkline_booking_value
	from erpatlas.command.portfolio import sparkline

	payload["portfolio"] = _portfolio_facts()
	payload["sparkline"] = sparkline(sparkline_booking_value())
	from erpatlas.command.forecast import linear_outlook, narrative_brief

	payload["outlook_30"] = linear_outlook(payload["sparkline"], horizon_days=30)
	payload["outlook_90"] = linear_outlook(payload["sparkline"], horizon_days=90)
	payload["brief"] = narrative_brief(payload)
	return payload


@frappe.whitelist()
def download_boardpack(company: str | None = None, project: str | None = None) -> None:
	"""PDF of the live Command JSON. Read-only — never writes Unit, PE, or Approval."""
	from frappe.utils.pdf import get_pdf

	from erpatlas.command.boardpack import render_boardpack

	payload = get_command(company, project)
	pack = render_boardpack(payload, as_of=str(today()))
	frappe.local.response.filename = pack["filename"]
	frappe.local.response.filecontent = get_pdf(pack["html"])
	frappe.local.response.type = "pdf"


def command_thresholds() -> dict:
	out = dict(DEFAULT_THRESHOLDS)
	if not frappe.db.exists("DocType", "Atlas Settings"):
		return out
	settings = frappe.get_single("Atlas Settings")
	for field, default in DEFAULT_THRESHOLDS.items():
		if not settings.meta.has_field(field):
			continue
		val = settings.get(field)
		if val in (None, ""):
			continue
		out[field] = val
	return out


def _handover_rows(project_names: set[str] | None) -> tuple[list, list]:
	if not frappe.db.exists("DocType", "Atlas Handover Case"):
		return [], []
	filters: dict = {}
	if project_names is not None:
		filters["project"] = ["in", list(project_names)]
	handovers = frappe.get_all(
		"Atlas Handover Case",
		filters=filters,
		fields=["name", "status", "occupancy_certificate", "snags_open", "project", "unit"],
	)
	snags = []
	if frappe.db.exists("DocType", "Atlas Snag"):
		sfilters: dict = {"status": "Open"}
		if project_names is not None:
			sfilters["project"] = ["in", list(project_names)]
		snags = frappe.get_all(
			"Atlas Snag",
			filters=sfilters,
			fields=["name", "status", "project", "unit", "handover"],
		)
	return handovers, snags


def _vendor_rows() -> list:
	if not frappe.get_meta("Supplier").has_field("atlas_stage"):
		return []
	return frappe.get_all(
		"Supplier",
		filters={"atlas_stage": ["!=", "Active"]},
		fields=["name", "atlas_stage", "supplier_name"],
	)


def _booking_rows(project_names: set[str] | None) -> tuple[list, list, list, list]:
	if not frappe.db.exists("DocType", "Atlas Booking"):
		return [], [], [], []
	filters: dict = {}
	if project_names is not None:
		filters["project"] = ["in", list(project_names)]
	bookings = frappe.get_all(
		"Atlas Booking",
		filters=filters,
		fields=[
			"name",
			"status",
			"total_consideration",
			"collected",
			"project",
			"channel_company",
			"creation",
		],
	)
	if not bookings:
		return [], [], [], []
	parents = [row.name for row in bookings]
	project_of = {row.name: row.project for row in bookings}
	steps = frappe.get_all(
		"Atlas Booking Payment Step",
		filters={"parent": ["in", parents]},
		fields=["parent", "gross", "collected"],
	)
	for step in steps:
		step["project"] = project_of.get(step.parent)
	commissions = []
	if frappe.db.exists("DocType", "Atlas Commission"):
		cfilters = {"status": ["in", ["Accrued", "Approved"]]}
		if project_names is not None:
			cfilters["project"] = ["in", list(project_names)]
		commissions = frappe.get_all(
			"Atlas Commission",
			filters=cfilters,
			fields=["name", "amount", "status", "project", "booking"],
		)
	payments = []
	if frappe.get_meta("Payment Entry").has_field("atlas_booking"):
		payments = frappe.get_all(
			"Payment Entry",
			filters={"docstatus": 1, "atlas_booking": ["in", parents]},
			fields=["name", "paid_amount", "posting_date", "atlas_booking", "project"],
		)
		for pe in payments:
			if not pe.get("project"):
				pe["project"] = project_of.get(pe.get("atlas_booking"))
	return bookings, steps, payments, commissions


def gl_cash_facts(company: str | None) -> dict | None:
	"""Read Bank + Cash GL and 90-day expense net / 3. None if GL is not there — do not invent."""
	if not company:
		return None
	if not frappe.db.exists("DocType", "GL Entry"):
		return None
	if not frappe.db.exists("DocType", "Account"):
		return None
	accounts = frappe.get_all(
		"Account",
		filters={"company": company, "account_type": ["in", ["Bank", "Cash"]], "is_group": 0},
		fields=["name", "account_type"],
	)
	if not accounts:
		return None
	bank_names = [a.name for a in accounts if a.account_type == "Bank"]
	cash_names = [a.name for a in accounts if a.account_type == "Cash"]
	return {
		"bank": _gl_balance(company, bank_names),
		"cash": _gl_balance(company, cash_names),
		"avg_monthly_outflow": _gl_avg_outflow(company),
	}


def _gl_balance(company: str, accounts: list[str]):
	if not accounts:
		return 0
	row = frappe.db.sql(
		"""
		select coalesce(sum(debit), 0) - coalesce(sum(credit), 0)
		from `tabGL Entry`
		where account in %s and company = %s and ifnull(is_cancelled, 0) = 0
		""",
		(accounts, company),
	)
	return row[0][0] if row else 0


def _gl_avg_outflow(company: str):
	from frappe.utils import add_days

	names = frappe.get_all(
		"Account",
		filters={"company": company, "root_type": "Expense", "is_group": 0},
		pluck="name",
	)
	if not names:
		return 0
	start = add_days(today(), -90)
	row = frappe.db.sql(
		"""
		select coalesce(sum(debit), 0) - coalesce(sum(credit), 0)
		from `tabGL Entry`
		where account in %s and company = %s and posting_date >= %s
			and ifnull(is_cancelled, 0) = 0
		""",
		(names, company, start),
	)
	net = row[0][0] if row else 0
	return float(net or 0) / 3
