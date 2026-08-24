"""Site diary and inspection rules. No frappe."""

from __future__ import annotations

PASS = "Pass"
FAIL = "Fail"
PENDING = "Pending"
INSPECTION_RESULTS = (PENDING, PASS, FAIL)


def diary_key(*, project: str, diary_date: str, device_key: str) -> str:
	return f"{project}::{diary_date}::{device_key}"


def refuse_diary(*, already_sealed: bool) -> str | None:
	if already_sealed:
		return "A diary for this device and date already exists."
	return None


def refuse_complete(*, current: str | None, result: str) -> str | None:
	if current != PENDING:
		return "Inspection is already complete."
	if result not in (PASS, FAIL):
		return "Inspection result must be Pass or Fail."
	return None


def ncr_from_fail(*, template: str, location: str) -> dict:
	return {
		"kind": "ncr",
		"title": f"NCR from {template} @ {location}",
		"status": "corrective",
		"raises_approval": False,
	}
