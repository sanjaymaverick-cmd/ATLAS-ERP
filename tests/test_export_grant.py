from erpatlas.approvals.queue import APPROVED, REJECTED, refuse_self_approve
from erpatlas.documents.grant import (
	DOC_ISSUED,
	DOC_QUARANTINE,
	GRANT_GRANTED,
	GRANT_PENDING,
	GRANT_USED,
	grant_status_on_decision,
	refuse_consume,
	refuse_request_export,
)


def test_quarantine_cannot_export():
	assert "Quarantine" in refuse_request_export(doc_status=DOC_QUARANTINE, existing_live=False)
	assert refuse_request_export(doc_status=DOC_ISSUED, existing_live=False) is None


def test_one_live_grant_per_file():
	assert "already open" in refuse_request_export(doc_status=DOC_ISSUED, existing_live=True)


def test_consume_is_single_use_and_only_when_granted():
	assert refuse_consume(grant_status=GRANT_GRANTED) is None
	assert "already been used" in refuse_consume(grant_status=GRANT_USED)
	assert "not authorised" in refuse_consume(grant_status=GRANT_PENDING)
	assert "not authorised" in refuse_consume(grant_status="Rejected")


def test_approval_sets_granted_or_rejected():
	assert grant_status_on_decision(APPROVED) == GRANT_GRANTED
	assert grant_status_on_decision(REJECTED) == "Rejected"


def test_four_eyes_requester_cannot_approve_even_if_md():
	assert refuse_self_approve(
		kind="Document export", requested_by="md@atlas.local", actor="md@atlas.local"
	)
	assert (
		refuse_self_approve(
			kind="Document export", requested_by="docs@atlas.local", actor="pd@atlas.local"
		)
		is None
	)
