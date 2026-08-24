"""Collection waits for Approval kind Payment. The Payment Entry is created only on Approved."""

from __future__ import annotations


def refuse_request_payment(*, pending: bool) -> str | None:
	if pending:
		return "This collection is already waiting in Approvals."
	return None


def payment_waiting_on() -> str:
	return "Finance Lead"


def payment_context(*, amount, mode_of_payment: str | None, step_idx) -> dict:
	return {
		"amount": str(amount),
		"mode_of_payment": mode_of_payment or "",
		"step_idx": step_idx,
	}
