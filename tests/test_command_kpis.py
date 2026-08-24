"""Command P0 — exception-first counts. No site, no cash KPIs."""

from erpatlas.command.kpis import (
	COMMAND_ROLES,
	DEFAULT_APPROVAL_SLA_DAYS,
	build_command,
	count_units_by_status,
	exception_queue,
	holds_expiring_soon,
	refuse_command_access,
)
from erpatlas.property_inventory.lock import AVAILABLE, BOOKED, HELD, SOLD


def test_only_md_and_project_director_open_command():
	assert refuse_command_access(["Atlas Developer Admin"]) is None
	assert refuse_command_access(["Atlas Project Director"]) is None
	assert "Channel" in refuse_command_access(["Atlas Channel Agent"])
	assert "Channel" in refuse_command_access(["Atlas Channel Admin", "Atlas Developer Admin"])
	assert "Command is for" in refuse_command_access(["Atlas Finance"])
	assert "Command is for" in refuse_command_access(["Atlas Sales Manager"])
	assert refuse_command_access(["Administrator", "Atlas Channel Agent", "Atlas Developer Admin"]) is None
	assert COMMAND_ROLES == {"Atlas Developer Admin", "Atlas Project Director"}


def test_unit_counts_include_every_status_zero():
	counts = count_units_by_status(
		[{"status": AVAILABLE}, {"status": AVAILABLE}, {"status": HELD}, {"status": BOOKED}]
	)
	assert counts[AVAILABLE] == 2
	assert counts[HELD] == 1
	assert counts[BOOKED] == 1
	assert counts[SOLD] == 0
	assert counts["Dispute"] == 0


def test_holds_expiring_soon_use_inclusive_until():
	holds = [
		{"status": "Held", "until": "2026-08-24", "project": "P1"},
		{"status": "Held", "until": "2026-08-26", "project": "P1"},
		{"status": "Held", "until": "2026-08-27", "project": "P1"},
		{"status": "Released", "until": "2026-08-24", "project": "P1"},
		{"status": "Held", "until": None, "project": "P1"},
	]
	soon = holds_expiring_soon(holds, "2026-08-24", within_days=2)
	assert [h["until"] for h in soon] == ["2026-08-24", "2026-08-26"]


def test_exception_queue_is_pending_sorted_oldest_first_on_the_card():
	rows = [
		{"name": "AAP-1", "status": "Pending", "aging_days": 1, "title": "new"},
		{"name": "AAP-2", "status": "Approved", "aging_days": 40, "title": "done"},
		{"name": "AAP-3", "status": "Pending", "aging_days": 9, "title": "stale"},
	]
	board = build_command(units=[], holds=[], approvals=rows, today="2026-08-24")
	assert board["approvals"]["pending"] == 2
	assert board["approvals"]["past_sla"] == 1
	assert board["approvals"]["oldest_days"] == 9
	assert board["approvals"]["sla_days"] == DEFAULT_APPROVAL_SLA_DAYS
	assert [e["name"] for e in board["exceptions"]] == ["AAP-3", "AAP-1"]
	assert [e["name"] for e in exception_queue(board["exceptions"], limit=1)] == ["AAP-3"]


def test_legal_entity_filter_is_project_set_not_erpnext_company_on_the_unit():
	units = [
		{"status": AVAILABLE, "project": "Lake"},
		{"status": HELD, "project": "Ridge"},
	]
	holds = [{"status": "Held", "until": "2026-08-25", "project": "Lake"}]
	approvals = [{"status": "Pending", "aging_days": 4, "project": "Ridge", "name": "AAP-9"}]
	board = build_command(
		units=units,
		holds=holds,
		approvals=approvals,
		today="2026-08-24",
		project_names={"Lake"},
	)
	assert board["units"][AVAILABLE] == 1
	assert board["units"][HELD] == 0
	assert board["holds"]["held"] == 1
	assert board["approvals"]["pending"] == 0
	assert board["exceptions"] == []


def test_aging_falls_back_to_creation_date():
	board = build_command(
		units=[],
		holds=[],
		approvals=[{"name": "AAP-x", "status": "Pending", "creation": "2026-08-20 09:00:00"}],
		today="2026-08-24",
	)
	assert board["exceptions"][0]["aging_days"] == 4
	assert board["approvals"]["past_sla"] == 1


def test_command_never_invents_bank_cash_or_runway():
	board = build_command(units=[], holds=[], approvals=[], today="2026-08-24")
	assert board["shows_cash"] is False
	assert board["cash"] == {}
	assert "runway" not in board
	assert "cash" not in board["money"]


def test_booking_money_mtd_plan_and_commission_liability():
	from erpatlas.books.payment_gst import money

	board = build_command(
		units=[],
		holds=[
			{"status": "Booked", "project": "Lake"},
			{"status": "Released", "project": "Lake"},
			{"status": "Held", "until": "2026-08-28", "project": "Lake"},
		],
		approvals=[],
		today="2026-08-24",
		bookings=[
			{
				"name": "ABK-1",
				"status": "Active",
				"total_consideration": "1050000",
				"collected": "105000",
				"project": "Lake",
				"channel_company": "Pink City",
				"creation": "2026-08-10",
			},
			{
				"name": "ABK-2",
				"status": "Cancelled",
				"total_consideration": "900000",
				"collected": "0",
				"project": "Lake",
				"creation": "2026-08-11",
			},
			{
				"name": "ABK-3",
				"status": "Active",
				"total_consideration": "500000",
				"collected": "0",
				"project": "Lake",
				"channel_company": "",
				"creation": "2026-07-01",
			},
		],
		steps=[
			{"parent": "ABK-1", "project": "Lake", "gross": "1050000", "collected": "105000"},
			{"parent": "ABK-3", "project": "Lake", "gross": "500000", "collected": "0"},
		],
		payments=[{"posting_date": "2026-08-12", "paid_amount": "105000", "project": "Lake"}],
		commissions=[
			{"amount": "20000", "status": "Accrued", "project": "Lake"},
			{"amount": "1000", "status": "Paid", "project": "Lake"},
		],
	)
	m = board["money"]
	assert m["booking_value_live"] == money("1550000")
	assert m["booking_value_mtd"] == money("1050000")
	assert m["collections_mtd"] == money("105000")
	assert m["plan_gross"] == money("1550000")
	assert m["plan_collected"] == money("105000")
	assert m["receivable"] == money("1445000")
	assert m["commission_liability"] == money("20000")
	assert m["hold_conversion_pct"] == money("50")
	assert m["channel_bookings"] == 1
	assert m["in_house_bookings"] == 1
	assert board["shows_money"] is True
	assert board["shows_cash"] is False
