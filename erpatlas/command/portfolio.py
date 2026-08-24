"""Portfolio heat map. No frappe. Advise only — never posts money or locks a unit."""

from __future__ import annotations

from typing import Iterable, Mapping

from erpatlas.books.payment_gst import money

GREEN = "green"
AMBER = "amber"
RED = "red"


def project_health(
	*,
	open_ncrs: int = 0,
	pending_approvals: int = 0,
	diary_gap_days: int | None = None,
	receivable_pct=0,
) -> dict:
	drivers = []
	health = GREEN
	if int(open_ncrs or 0) > 0:
		health = RED
		drivers.append(f"{open_ncrs} failed work still open")
	if int(pending_approvals or 0) >= 3:
		health = RED
		drivers.append(f"{pending_approvals} Approvals waiting")
	pct = money(receivable_pct or 0)
	if diary_gap_days is not None and diary_gap_days >= 3:
		if health == GREEN:
			health = AMBER
		drivers.append(f"No site diary for {diary_gap_days} days")
	if pct >= money(20) and health != RED:
		health = AMBER
		drivers.append(f"Collection lag {pct}%")
	if not drivers:
		drivers.append("On track")
	return {"health": health, "drivers": drivers, "auto_action": False}


def heat_map(rows: Iterable[Mapping]) -> list[dict]:
	out = []
	for row in rows:
		card = project_health(
			open_ncrs=int(row.get("open_ncrs") or 0),
			pending_approvals=int(row.get("pending_approvals") or 0),
			diary_gap_days=row.get("diary_gap_days"),
			receivable_pct=row.get("receivable_pct") or 0,
		)
		out.append(
			{
				"project": row.get("project"),
				"health": card["health"],
				"drivers": card["drivers"],
				"auto_action": False,
			}
		)
	order = {RED: 0, AMBER: 1, GREEN: 2}
	return sorted(out, key=lambda r: (order.get(r["health"], 9), r.get("project") or ""))


def sparkline(values: Iterable) -> list:
	"""Last points for a strip. Empty is allowed."""
	return [money(v) for v in values]
