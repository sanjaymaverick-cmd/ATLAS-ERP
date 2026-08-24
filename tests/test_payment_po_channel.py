from erpatlas.booking.payment import refuse_request_payment
from erpatlas.booking.payment_handler import on_payment
from erpatlas.books.payment_gst import money
from erpatlas.channel.roster import refuse_bind
from erpatlas.command.kpis import build_command, cash_kpis
from erpatlas.commercial.po import on_purchase_order, refuse_request_po, refuse_submit_po
from erpatlas.property_inventory.lock import refuse_exclusive_hold


def test_collect_request_does_not_create_pe():
	assert refuse_request_payment(pending=True)
	assert refuse_request_payment(pending=False) is None
	assert "no booking" in on_payment({}, "Approved")
	assert on_payment({"ref_name": "ABK-1"}, "Rejected") is None


def test_po_submits_only_after_approval():
	assert "waits for a yes" in refuse_submit_po(approved=False, flagged=False)
	assert refuse_submit_po(approved=True, flagged=False) is None
	assert refuse_submit_po(approved=False, flagged=True) is None
	assert "Active" in refuse_request_po(pending=False, vendor_stage="Draft", already_submitted=False)
	assert refuse_request_po(pending=False, vendor_stage="Active", already_submitted=False) is None
	assert on_purchase_order({}, "Approved") == "Purchase order has no document."
	assert on_purchase_order({"ref_name": "PO-1"}, "Rejected") is None


def test_command_cash_only_from_gl_facts():
	empty = build_command(units=[], holds=[], approvals=[], today="2026-08-24")
	assert empty["shows_cash"] is False
	assert empty["cash"] == {}
	assert "cash" not in empty["money"]
	board = build_command(
		units=[],
		holds=[],
		approvals=[],
		today="2026-08-24",
		cash_board={"bank": "30", "cash": "10", "avg_monthly_outflow": "10"},
	)
	assert board["shows_cash"] is True
	assert board["cash"]["cash_position"] == money("40")
	assert board["cash"]["runway_months"] == money("4")
	assert board["cash"]["source"] == "gl"
	assert cash_kpis() is None


def test_exclusive_channel_and_agent_bind():
	assert refuse_exclusive_hold(exclusive_channel=None, hold_channel="Pink City") is None
	assert refuse_exclusive_hold(exclusive_channel="Pink City", hold_channel="Pink City") is None
	assert refuse_exclusive_hold(exclusive_channel="Pink City", hold_channel=None) is None
	assert "locked" in refuse_exclusive_hold(exclusive_channel="Pink City", hold_channel="Desert Reach")
	assert refuse_bind(user="", channel_company="Pink City")
	assert refuse_bind(user="agent@x", channel_company="Pink City") is None
