"""Export grant rules. No frappe. Four-eyes lives in approvals.queue.refuse_self_approve."""

from __future__ import annotations

from erpatlas.approvals.queue import APPROVED, REJECTED

DOC_QUARANTINE = "Quarantine"
DOC_REVIEW = "Review"
DOC_APPROVED = "Approved"
DOC_ISSUED = "Issued"
DOC_SUPERSEDED = "Superseded"
DOC_STATUSES = (DOC_QUARANTINE, DOC_REVIEW, DOC_APPROVED, DOC_ISSUED, DOC_SUPERSEDED)

GRANT_PENDING = "Pending"
GRANT_GRANTED = "Granted"
GRANT_USED = "Used"
GRANT_REJECTED = "Rejected"
GRANT_EXPIRED = "Expired"
GRANT_STATUSES = (GRANT_PENDING, GRANT_GRANTED, GRANT_USED, GRANT_REJECTED, GRANT_EXPIRED)
LIVE_GRANT = frozenset({GRANT_PENDING, GRANT_GRANTED})


def refuse_clear_quarantine(*, status: str) -> str | None:
	if status != DOC_QUARANTINE:
		return "Not in quarantine."
	return None


def refuse_issue(*, status: str) -> str | None:
	if status == DOC_QUARANTINE:
		return "Cannot issue a quarantined file."
	return None


def refuse_request_export(*, doc_status: str, existing_live: bool) -> str | None:
	if doc_status == DOC_QUARANTINE:
		return "Quarantined files cannot be exported."
	if existing_live:
		return "An export request is already open for this file."
	return None


def refuse_consume(*, grant_status: str) -> str | None:
	if grant_status == GRANT_USED:
		return "This grant has already been used."
	if grant_status != GRANT_GRANTED:
		return "This download is not authorised."
	return None


def grant_status_on_decision(decision: str) -> str:
	if decision == APPROVED:
		return GRANT_GRANTED
	if decision == REJECTED:
		return GRANT_REJECTED
	return GRANT_PENDING
