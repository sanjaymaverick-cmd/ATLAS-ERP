"""Command P0 calculators. No frappe. Never posts money or decisions."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable, Mapping

from erpatlas.approvals.queue import PENDING
from erpatlas.property_inventory.lock import CHANNEL_ROLES, HOLD_HELD, UNIT_STATUSES

COMMAND_ROLES = frozenset({"Atlas Developer Admin", "Atlas Project Director"})

# P2 will read these from Atlas Settings. P0 uses closed defaults.
DEFAULT_APPROVAL_SLA_DAYS = 3
DEFAULT_HOLD_EXPIRING_DAYS = 2
EXCEPTION_LIMIT = 15


def refuse_command_access(roles: Iterable[str]) -> str | None:
	role_set = set(roles)
	if role_set & CHANNEL_ROLES:
		return "Channel seats cannot open Command."
	if not role_set & COMMAND_ROLES:
		return "Command is for Atlas Developer Admin and Atlas Project Director."
	return None


def add_iso_days(today: str, days: int) -> str:
	return (date.fromisoformat(today) + timedelta(days=days)).isoformat()


def filter_by_projects(rows: Iterable[Mapping], project_names: set[str] | None) -> list[dict]:
	items = [dict(r) for r in rows]
	if project_names is None:
		return items
	return [r for r in items if r.get("project") in project_names]


def count_units_by_status(units: Iterable[Mapping]) -> dict[str, int]:
	counts = {status: 0 for status in UNIT_STATUSES}
	for unit in units:
		status = unit.get("status")
		if status in counts:
			counts[status] += 1
	return counts


def aging_days_of(row: Mapping, today: str) -> int:
	if row.get("aging_days") not in (None, ""):
		return int(row["aging_days"])
	created = str(row.get("creation") or "")[:10]
	if not created:
		return 0
	return (date.fromisoformat(today) - date.fromisoformat(created)).days


def live_holds(holds: Iterable[Mapping]) -> list[dict]:
	return [dict(h) for h in holds if h.get("status") == HOLD_HELD]


def holds_expiring_soon(holds: Iterable[Mapping], today: str, within_days: int) -> list[dict]:
	"""Held rows whose inclusive `until` falls between today and today+within_days."""
	end = add_iso_days(today, within_days)
	out = []
	for hold in live_holds(holds):
		until = hold.get("until")
		if until and today <= str(until) <= end:
			out.append(hold)
	return out


def approval_aging(approvals: Iterable[Mapping], today: str, sla_days: int) -> dict:
	pending = []
	for row in approvals:
		if row.get("status") != PENDING:
			continue
		item = dict(row)
		item["aging_days"] = aging_days_of(item, today)
		pending.append(item)
	past = [a for a in pending if a["aging_days"] >= sla_days]
	oldest = max((a["aging_days"] for a in pending), default=0)
	return {
		"pending": len(pending),
		"past_sla": len(past),
		"oldest_days": oldest,
		"pending_rows": pending,
	}


def exception_queue(pending_rows: Iterable[Mapping], *, limit: int = EXCEPTION_LIMIT) -> list[dict]:
	ordered = sorted(pending_rows, key=lambda a: int(a.get("aging_days") or 0), reverse=True)
	return [dict(a) for a in ordered[:limit]]


def build_command(
	*,
	units: Iterable[Mapping],
	holds: Iterable[Mapping],
	approvals: Iterable[Mapping],
	today: str,
	project_names: set[str] | None = None,
	sla_days: int = DEFAULT_APPROVAL_SLA_DAYS,
	hold_expiring_days: int = DEFAULT_HOLD_EXPIRING_DAYS,
) -> dict:
	"""Exception-first payload. No cash, no runway, no writes."""
	units_f = filter_by_projects(units, project_names)
	holds_f = filter_by_projects(holds, project_names)
	approvals_f = filter_by_projects(approvals, project_names)
	aging = approval_aging(approvals_f, today, sla_days)
	held = live_holds(holds_f)
	expiring = holds_expiring_soon(holds_f, today, hold_expiring_days)
	return {
		"units": count_units_by_status(units_f),
		"holds": {"held": len(held), "expiring_soon": len(expiring)},
		"approvals": {
			"pending": aging["pending"],
			"past_sla": aging["past_sla"],
			"oldest_days": aging["oldest_days"],
			"sla_days": sla_days,
		},
		"exceptions": exception_queue(aging["pending_rows"]),
		"shows_cash": False,
	}
