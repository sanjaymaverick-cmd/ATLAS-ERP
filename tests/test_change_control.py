from erpatlas.change_control.flow import (
	CLOSED,
	REVIEW,
	refuse_close_ncr,
	refuse_respond,
	rfi_sla_overdue,
	status_after_respond,
	vo_needs_amount,
)
from erpatlas.change_control.handler import on_change


def test_rfi_response_closes():
	assert refuse_respond(kind="rfi", response="", status="open")
	assert refuse_respond(kind="rfi", response="Answered", status="closed")
	assert refuse_respond(kind="rfi", response="Answered", status="open") is None
	assert status_after_respond("rfi") == CLOSED
	assert status_after_respond("ncr") == REVIEW


def test_ncr_close_needs_pass_reinspection():
	assert refuse_close_ncr(kind="rfi", status="open")
	assert "Pass re-inspection" in refuse_close_ncr(kind="ncr", status="corrective")
	assert "Pass re-inspection" in refuse_close_ncr(
		kind="ncr", status="corrective", reinspection_result="Fail"
	)
	assert refuse_close_ncr(kind="ncr", status="corrective", reinspection_result="Pass") is None
	assert refuse_close_ncr(kind="ncr", status="closed", reinspection_result="Pass")


def test_vo_amount_and_change_handler_never_pays():
	assert "amount" in vo_needs_amount("change", None)
	assert vo_needs_amount("ncr", None) is None
	assert on_change({}, "Approved") == "Change has no row."
	assert rfi_sla_overdue(kind="rfi", sla_hours=8, aging_hours=8)
	assert not rfi_sla_overdue(kind="rfi", sla_hours=8, aging_hours=3)
	assert not rfi_sla_overdue(kind="ncr", sla_hours=8, aging_hours=99)
