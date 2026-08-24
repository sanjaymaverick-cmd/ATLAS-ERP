"""Company-accounts recon cases. Atlas never posts a voucher. Not Tally."""

from __future__ import annotations

OPEN = "open"
REVIEW = "review"
RECONCILED = "reconciled"
EXCEPTION = "exception"
CASE_STATUSES = (OPEN, REVIEW, RECONCILED, EXCEPTION)
SETTLE = (RECONCILED, EXCEPTION)


def refuse_settle(*, status: str | None, decision: str | None, note: str | None) -> str | None:
	if status in (RECONCILED, EXCEPTION):
		return "This case is already closed."
	if decision not in SETTLE:
		return "Settle as reconciled or exception."
	if decision == EXCEPTION and not str(note or "").strip():
		return "Exception needs a written acceptance."
	return None


def settle_effects(decision: str) -> dict:
	return {
		"status": decision,
		"creates_payment_entry": False,
		"creates_journal_entry": False,
		"posts_to_tally": False,
	}
