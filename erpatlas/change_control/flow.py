"""RFI / NCR / VO status. Money VO goes to Approvals. No Payment Entry."""

from __future__ import annotations

def refuse_close_ncr(*, kind: str, status: str) -> str | None:
	if kind != "ncr":
		return "Not an NCR."
	if status == "closed":
		return "This failed work is already closed."
	return None


def vo_needs_amount(kind: str, amount) -> str | None:
	if kind != "change":
		return None
	if amount in (None, ""):
		return "Variation needs an amount for the Approval card."
	return None
