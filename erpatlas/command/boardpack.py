"""Printable Command board pack from structured JSON. No frappe. Never writes Unit, PE, or Approval."""

from __future__ import annotations

import html
from typing import Mapping

from erpatlas.command.forecast import MODEL_ID

DISCLAIMER = (
	"Advisory only — Command does not approve, pay, or change a unit. "
	"This pack is a read-only snapshot. Not CatBoost."
)


def _esc(value) -> str:
	if value is None:
		return ""
	return html.escape(str(value), quote=True)


def feature_summary(board: Mapping) -> dict:
	units = board.get("units") or {}
	money_board = board.get("money") or {}
	approvals = board.get("approvals") or {}
	outlook = board.get("outlook_30") or {}
	return {
		"available": units.get("Available") or 0,
		"held": units.get("Held") or 0,
		"booked": units.get("Booked") or 0,
		"sold": units.get("Sold") or 0,
		"pending_approvals": approvals.get("pending") or 0,
		"booking_value_live": money_board.get("booking_value_live") or 0,
		"risk_count": len(board.get("risk") or []),
		"model_id": outlook.get("model_id") or MODEL_ID,
	}


def render_boardpack(board: Mapping, *, as_of: str) -> dict:
	"""HTML + audit fields from Command JSON. Never posts money or decisions."""
	outlook = board.get("outlook_30") or {}
	model_id = outlook.get("model_id") or MODEL_ID
	summary = feature_summary(board)
	return {
		"html": _html(board, as_of=as_of, model_id=model_id),
		"as_of": as_of,
		"model_id": model_id,
		"feature_summary": summary,
		"filename": f"command-boardpack-{as_of}.pdf",
		"auto_action": False,
		"writes_unit": False,
		"creates_payment_entry": False,
		"decides_approval": False,
		"served_by": model_id,
	}


def _html(board: Mapping, *, as_of: str, model_id: str) -> str:
	filters = board.get("filters") or {}
	legal = _esc(filters.get("company") or "All Legal Entities")
	project = _esc(filters.get("project") or "All projects")
	sections = [
		_heading(as_of=as_of, legal=legal, project=project, model_id=model_id),
		_exceptions(board),
		_risks(board),
		_portfolio(board),
		_outlook(board, model_id=model_id),
		_money(board),
		_inventory(board),
		_approvals(board),
		f'<p class="disclaimer">{_esc(DISCLAIMER)}</p>',
	]
	body = "\n".join(sections)
	return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Command board pack — {_esc(as_of)}</title>
<style>
body {{ font-family: Helvetica, Arial, sans-serif; font-size: 11pt; color: #111; margin: 24px; }}
h1 {{ font-size: 16pt; margin: 0 0 4px; }}
h2 {{ font-size: 11pt; letter-spacing: 0.04em; text-transform: uppercase; margin: 1.3em 0 0.4em; }}
.muted {{ color: #555; font-size: 9pt; }}
table {{ width: 100%; border-collapse: collapse; margin: 0 0 8px; }}
th, td {{ border: 1px solid #ccc; padding: 6px 8px; text-align: left; vertical-align: top; }}
th {{ background: #f2f2f2; font-size: 9pt; text-transform: uppercase; letter-spacing: 0.04em; }}
.kpi td {{ width: 25%; }}
.red {{ color: #a11; }}
.disclaimer {{ margin-top: 1.6em; font-size: 9pt; color: #444; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def _heading(*, as_of: str, legal: str, project: str, model_id: str) -> str:
	return (
		"<h1>Command board pack</h1>"
		f'<p class="muted">As of {_esc(as_of)} · Legal Entity: {legal} · Project: {project} · '
		f"Outlook model: {_esc(model_id)}</p>"
		'<p>Waiting for a yes drives the day. Green totals are secondary.</p>'
	)


def _kpi_table(rows: list[tuple[str, object]]) -> str:
	cells = "".join(
		f"<td><strong>{_esc(label)}</strong><br/>{_esc(value)}</td>" for label, value in rows
	)
	return f'<table class="kpi"><tr>{cells}</tr></table>'


def _exceptions(board: Mapping) -> str:
	rows = board.get("exceptions") or []
	if not rows:
		body = "<p class=\"muted\">No pending Approvals in this filter.</p>"
	else:
		items = ["<table><tr><th>Kind</th><th>Title</th><th>Waiting on</th><th>Aging</th><th>Project</th></tr>"]
		for row in rows:
			items.append(
				"<tr>"
				f"<td>{_esc(row.get('kind'))}</td>"
				f"<td>{_esc(row.get('title') or row.get('name'))}</td>"
				f"<td>{_esc(row.get('waiting_on'))}</td>"
				f"<td>{_esc(row.get('aging_days') or 0)}d</td>"
				f"<td>{_esc(row.get('project'))}</td>"
				"</tr>"
			)
		items.append("</table>")
		body = "".join(items)
	return f"<h2>Waiting for a yes</h2>{body}"


def _risks(board: Mapping) -> str:
	rows = board.get("risk") or []
	if not rows:
		body = "<p class=\"muted\">No risk cards in this filter.</p>"
	else:
		items = ["<table><tr><th>Domain</th><th>Severity</th><th>Title</th><th>Driver</th><th>Waiting on</th></tr>"]
		for row in rows:
			sev = _esc(row.get("severity"))
			cls = ' class="red"' if row.get("severity") == "red" else ""
			items.append(
				"<tr>"
				f"<td>{_esc(row.get('domain'))}</td>"
				f"<td{cls}>{sev}</td>"
				f"<td>{_esc(row.get('title'))}</td>"
				f"<td>{_esc(row.get('driver'))}</td>"
				f"<td>{_esc(row.get('waiting_on'))}</td>"
				"</tr>"
			)
		items.append("</table>")
		body = "".join(items)
	return (
		"<h2>Risk</h2>"
		'<p class="muted">Deterministic thresholds. Cards advise only — they do not approve, pay, or change a unit.</p>'
		f"{body}"
	)


def _portfolio(board: Mapping) -> str:
	rows = board.get("portfolio") or []
	spark = board.get("sparkline") or []
	spark_line = ""
	if spark:
		spark_line = f'<p class="muted">Live booking value strip: {_esc(" · ".join(str(p) for p in spark))}</p>'
	if not rows:
		body = "<p class=\"muted\">No projects in this filter.</p>"
	else:
		items = ["<table><tr><th>Project</th><th>Health</th><th>Driver</th></tr>"]
		for row in rows:
			drivers = row.get("drivers") or []
			items.append(
				"<tr>"
				f"<td>{_esc(row.get('project'))}</td>"
				f"<td>{_esc(row.get('health'))}</td>"
				f"<td>{_esc(drivers[0] if drivers else '')}</td>"
				"</tr>"
			)
		items.append("</table>")
		body = "".join(items)
	return f"<h2>Portfolio</h2>{spark_line}{body}"


def _outlook(board: Mapping, *, model_id: str) -> str:
	o30 = board.get("outlook_30") or {}
	o90 = board.get("outlook_90") or {}
	brief = board.get("brief") or []
	kpis = _kpi_table(
		[
			("30d booking value", o30.get("projected") if o30.get("projected") is not None else "—"),
			("90d booking value", o90.get("projected") if o90.get("projected") is not None else "—"),
		]
	)
	lines = "".join(f"<p>{_esc(line)}</p>" for line in brief)
	return (
		"<h2>Outlook</h2>"
		f'<p class="muted">Linear read-only forecast from snapshots ({_esc(model_id)}). Not CatBoost. Does not pay, lock, or decide.</p>'
		f"{kpis}{lines}"
	)


def _money(board: Mapping) -> str:
	if not board.get("shows_money"):
		return ""
	money_board = board.get("money") or {}
	pct = money_board.get("hold_conversion_pct")
	kpis = _kpi_table(
		[
			("Live booking value", money_board.get("booking_value_live") or 0),
			("Booking value MTD", money_board.get("booking_value_mtd") or 0),
			("Collected MTD", money_board.get("collections_mtd") or 0),
			("Receivable", money_board.get("receivable") or 0),
		]
	)
	more = _kpi_table(
		[
			("Plan", money_board.get("plan_gross") or 0),
			("Collected on plan", money_board.get("plan_collected") or 0),
			("Commission accrued", money_board.get("commission_liability") or 0),
			("Hold → book", "—" if pct is None else f"{pct}%"),
		]
	)
	mix = _kpi_table(
		[
			("Channel bookings", money_board.get("channel_bookings") or 0),
			("In-house bookings", money_board.get("in_house_bookings") or 0),
		]
	)
	return (
		"<h2>Sales and collections</h2>"
		'<p class="muted">From Atlas Booking and Payment Entry. Not bank cash, not runway.</p>'
		f"{kpis}{more}{mix}"
	)


def _inventory(board: Mapping) -> str:
	units = board.get("units") or {}
	holds = board.get("holds") or {}
	kpis = _kpi_table(
		[
			("Available", units.get("Available") or 0),
			("Held", units.get("Held") or 0),
			("Booked", units.get("Booked") or 0),
			("Sold", units.get("Sold") or 0),
		]
	)
	hold_kpis = _kpi_table(
		[
			("Live holds", holds.get("held") or 0),
			("Holds expiring soon", holds.get("expiring_soon") or 0),
		]
	)
	return f"<h2>Inventory and holds</h2>{kpis}{hold_kpis}"


def _approvals(board: Mapping) -> str:
	approvals = board.get("approvals") or {}
	kpis = _kpi_table(
		[
			("Pending", approvals.get("pending") or 0),
			("Past SLA", approvals.get("past_sla") or 0),
			("Oldest (days)", approvals.get("oldest_days") or 0),
			("SLA (days)", approvals.get("sla_days") or 0),
		]
	)
	return f"<h2>Approvals</h2>{kpis}"
