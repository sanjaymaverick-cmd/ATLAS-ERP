from erpatlas.books.payment_gst import money
from erpatlas.controls.quantity import (
	APPROVED,
	PROVISIONAL,
	VARIANCE,
	derived_status,
	refuse_approve,
	refuse_edit_locked,
	refuse_qty,
	variance_qty,
)
from erpatlas.controls.stock import refuse_issue


def test_mismatch_is_variance_and_match_is_provisional():
	assert derived_status(drawing_qty="100", site_qty="100") == PROVISIONAL
	assert derived_status(drawing_qty="100", site_qty="110") == VARIANCE
	assert derived_status(drawing_qty="100", site_qty="90") == VARIANCE
	assert derived_status(drawing_qty="100", site_qty="110", status=APPROVED) == APPROVED
	assert variance_qty(drawing_qty="100", site_qty="110") == money("10")
	assert variance_qty(drawing_qty="100", site_qty="90") == money("-10")


def test_approve_locks_and_does_not_pay():
	assert refuse_approve(status=VARIANCE) is None
	assert refuse_approve(status=PROVISIONAL) is None
	assert "already approved" in refuse_approve(status=APPROVED)
	assert "locked" in refuse_edit_locked(status=APPROVED)
	assert refuse_edit_locked(status=VARIANCE) is None
	assert refuse_qty(qty="-1")
	assert refuse_qty(qty="0") is None


def test_material_issue_gate_is_unchanged():
	assert "more than accepted" in refuse_issue(received="10", issued="8", qty="3")
