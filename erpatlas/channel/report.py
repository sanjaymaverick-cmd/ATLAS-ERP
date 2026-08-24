"""Daily report rules. No frappe. Hold gate lives in property_inventory.lock."""

from __future__ import annotations

from typing import Iterable


def report_key(*, agent: str, report_date: str) -> str:
	return f"{agent}::{report_date}"


def refuse_second_report(*, already_filed_today: bool) -> str | None:
	if already_filed_today:
		return "Today’s report is already filed for this agent."
	return None


def filed_today(reports: Iterable[dict], *, agent: str, today: str) -> bool:
	key = report_key(agent=agent, report_date=today)
	return any(
		r.get("report_key") == key
		or (r.get("agent") == agent and str(r.get("report_date") or "") == today)
		for r in reports
	)
