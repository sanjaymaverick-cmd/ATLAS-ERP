"""RFI / NCR / VO status. Money VO goes to Approvals. No Payment Entry."""

from __future__ import annotations

from erpatlas.site.gates import PASS

RFI = "rfi"
NCR = "ncr"
CHANGE = "change"

OPEN = "open"
CORRECTIVE = "corrective"
REVIEW = "review"
APPROVED = "approved"
REJECTED = "rejected"
CLOSED = "closed"


def refuse_respond(*, kind: str, response: str | None, status: str | None) -> str | None:
	if status == CLOSED:
		return "This item is already closed."
	if not str(response or "").strip():
		return "Response required."
	return None


def status_after_respond(kind: str) -> str:
	if kind == RFI:
		return CLOSED
	return REVIEW


def refuse_close_ncr(*, kind: str, status: str, reinspection_result: str | None = None) -> str | None:
	if kind != NCR:
		return "Not an NCR."
	if status == CLOSED:
		return "This failed work is already closed."
	if reinspection_result != PASS:
		return "Close NCR only after a Pass re-inspection."
	return None


def vo_needs_amount(kind: str, amount) -> str | None:
	if kind != CHANGE:
		return None
	if amount in (None, ""):
		return "Variation needs an amount for the Approval card."
	return None


def rfi_sla_overdue(*, kind: str, sla_hours, aging_hours) -> bool:
	if kind != RFI:
		return False
	try:
		limit = float(sla_hours)
	except (TypeError, ValueError):
		return False
	if limit <= 0:
		return False
	return float(aging_hours or 0) >= limit
