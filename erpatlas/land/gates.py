"""Statutory obligation rules. No frappe. RERA 70/30 bank split is not here."""

from __future__ import annotations


def refuse_file(*, status: str) -> str | None:
	if status == "filed":
		return "This obligation is already filed."
	return None


def overdue(*, status: str, due: str, today: str) -> bool:
	if status == "filed":
		return False
	return bool(due) and due < today
