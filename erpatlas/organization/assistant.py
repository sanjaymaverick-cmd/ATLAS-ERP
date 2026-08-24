"""Assistant is draft-only. Never pays, never locks a unit, never decides Approvals."""

from __future__ import annotations

DRAFT = "draft"


def refuse_execute(*, status: str) -> str | None:
	return "Assistant notes are draft-only. A person must act in Approvals, Booking, or Books."


def stamp_draft(note: str) -> dict:
	return {
		"status": DRAFT,
		"body": note,
		"creates_payment_entry": False,
		"writes_unit": False,
		"decides_approval": False,
	}
