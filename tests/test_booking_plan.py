"""Atlas Booking activate / collect / commission — Atlas-3 + research/02 + /06."""

from decimal import Decimal

from erpatlas.booking.plan import (
	ACTIVE,
	CANCELLED,
	COMMISSION_ACCRUED,
	DRAFT,
	POSSESSION,
	accrue_intent,
	activate_plan,
	booking_live_unit,
	commission_amount,
	default_steps,
	next_collect_step,
	refuse_activate,
	refuse_cancel,
	refuse_collect_booking,
	refuse_step_percents,
)
from erpatlas.books.payment_gst import INCLUSIVE, money
from erpatlas.property_inventory.lock import AVAILABLE, BOOKED, HELD, LIVE_BOOKING, SOLD


def test_default_steps_are_one_hundred():
	assert refuse_step_percents(default_steps()) is None
	assert refuse_step_percents([]) == "Payment schedule needs at least one step."
	assert "100" in refuse_step_percents([{"percent": "40"}, {"percent": "40"}])


def test_refuse_activate_needs_customer_money_and_bookable_unit():
	ok = dict(
		unit_status=HELD,
		code="A-101",
		live_booking=False,
		customer="Yadav",
		consideration="1000000",
		steps=default_steps(),
		booking_status=DRAFT,
	)
	assert refuse_activate(**ok) is None
	assert refuse_activate(**{**ok, "unit_status": AVAILABLE}) is None
	assert "Sold" in refuse_activate(**{**ok, "unit_status": SOLD})
	assert "active booking" in refuse_activate(**{**ok, "live_booking": True})
	assert "customer" in refuse_activate(**{**ok, "customer": ""})
	assert "greater than zero" in refuse_activate(**{**ok, "consideration": "0"})
	assert "already Active" in refuse_activate(**{**ok, "booking_status": ACTIVE})


def test_activate_plan_books_unit_and_expands_gst():
	plan = activate_plan(
		consideration="1050000",
		rate=5,
		tax_included=INCLUSIVE,
		steps=[
			{"label": "Token", "kind": "booking", "percent": "10"},
			{"label": "Slab", "kind": "slab", "percent": "90"},
		],
	)
	assert plan["unit_to"] == BOOKED
	assert plan["hold_to"] == "Booked"
	assert plan["booking_status"] == ACTIVE
	assert plan["grand_total"] == money("1050000")
	assert plan["taxable_total"] == money("1000000")
	assert plan["steps"][0]["gross"] == money("105000")


def test_live_booking_unique_key_is_the_unit_while_active_or_possession():
	assert booking_live_unit(status=ACTIVE, unit="AUN-1", booking_name="ABK-1") == "AUN-1"
	assert booking_live_unit(status=POSSESSION, unit="AUN-1", booking_name="ABK-1") == "AUN-1"
	assert set(LIVE_BOOKING) == {ACTIVE, POSSESSION}
	assert booking_live_unit(status=DRAFT, unit="AUN-1", booking_name="ABK-1") == "ABK-1"
	assert booking_live_unit(status=CANCELLED, unit="AUN-1", booking_name="ABK-1") == "ABK-1"


def test_in_house_does_not_accrue_commission():
	assert accrue_intent(
		channel_company=None,
		channel_status=None,
		rate=2,
		consideration="1000000",
		already_accrued=False,
	) is None


def test_active_channel_accrues_percent_as_accrued_never_a_payment_entry():
	row = accrue_intent(
		channel_company="Pink City",
		channel_status="Active",
		rate="2",
		consideration="1000000",
		already_accrued=False,
	)
	assert row == {
		"amount": money("20000"),
		"status": COMMISSION_ACCRUED,
		"creates_payment_entry": False,
	}
	assert commission_amount("1000000", "2.5") == money("25000")


def test_invited_suspended_or_duplicate_does_not_accrue():
	base = dict(
		channel_company="Pink City",
		rate="2",
		consideration="1000000",
		already_accrued=False,
	)
	assert accrue_intent(**{**base, "channel_status": "Invited"}) is None
	assert accrue_intent(**{**base, "channel_status": "Suspended"}) is None
	assert accrue_intent(**{**base, "channel_status": "Active", "already_accrued": True}) is None
	assert accrue_intent(**{**base, "channel_status": "Active", "rate": "0"}) is None


def test_collect_cancelled_or_draft_or_over_step_refused():
	step = {"gross": "100", "collected": "0"}
	assert (
		refuse_collect_booking(
			status=ACTIVE, step=step, receipt="100", plan_collected="0", plan_gross="200"
		)
		is None
	)
	assert "Cancelled" in refuse_collect_booking(
		status=CANCELLED, step=step, receipt="10", plan_collected="0", plan_gross="200"
	)
	assert "Active" in refuse_collect_booking(
		status=DRAFT, step=step, receipt="10", plan_collected="0", plan_gross="200"
	)
	assert "already collected" in refuse_collect_booking(
		status=ACTIVE, step=None, receipt="10", plan_collected="200", plan_gross="200"
	)
	assert "exceed" in refuse_collect_booking(
		status=ACTIVE, step=step, receipt="150", plan_collected="0", plan_gross="200"
	)


def test_next_collect_step_is_first_unpaid():
	steps = [
		{"idx": 0, "gross": "100", "collected": "100"},
		{"idx": 1, "gross": "200", "collected": "0"},
	]
	nxt = next_collect_step(steps)
	assert nxt and nxt["idx"] == 1


def test_cancel_blocked_on_possession_and_when_money_posted():
	assert (
		refuse_cancel(status=ACTIVE, unit_status=BOOKED, has_posted_money=False) is None
	)
	assert "Possession" in refuse_cancel(status=POSSESSION, unit_status=SOLD, has_posted_money=False)
	assert "Possession" in refuse_cancel(status=ACTIVE, unit_status=SOLD, has_posted_money=False)
	assert "Finance" in refuse_cancel(status=ACTIVE, unit_status=BOOKED, has_posted_money=True)
	assert "Active" in refuse_cancel(status=DRAFT, unit_status=HELD, has_posted_money=False)
