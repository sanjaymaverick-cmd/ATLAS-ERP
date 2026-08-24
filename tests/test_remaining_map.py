from erpatlas.change_control.flow import refuse_close_ncr, vo_needs_amount
from erpatlas.communications.templates import refuse_register, refuse_send
from erpatlas.land.gates import overdue, refuse_file
from erpatlas.organization.assistant import refuse_execute, stamp_draft


def test_ncr_close_and_vo_amount():
	assert refuse_close_ncr(kind="rfi", status="open")
	assert refuse_close_ncr(kind="ncr", status="corrective") is None
	assert "amount" in vo_needs_amount("change", None)
	assert vo_needs_amount("ncr", None) is None


def test_assistant_is_draft_only():
	assert "draft-only" in refuse_execute(status="draft")
	note = stamp_draft("Suggest a hold")
	assert note["creates_payment_entry"] is False
	assert note["writes_unit"] is False
	assert note["decides_approval"] is False


def test_whatsapp_registers_does_not_send():
	assert "Sending" in refuse_send()
	assert refuse_register(name="Visit", body="Hello {name}") is None


def test_obligation_overdue():
	assert overdue(status="open", due="2026-08-01", today="2026-08-24")
	assert not overdue(status="filed", due="2026-08-01", today="2026-08-24")
	assert refuse_file(status="filed")
