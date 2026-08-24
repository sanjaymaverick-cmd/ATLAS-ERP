"""Atlas-3 Phase 1 inventory acceptance, as pure rules."""

from erpatlas.property_inventory.lock import (
	AVAILABLE,
	BOOKED,
	DISPUTE,
	HELD,
	HOLD_BOOKED,
	HOLD_HELD,
	SOLD,
	channel_needs_booking_approval,
	holds_due_to_expire,
	live_unit_key,
	refuse_book,
	refuse_dispute,
	refuse_hold,
	refuse_hold_without_report,
	refuse_transition,
	unit_status_on_hold_expire,
)


def test_hold_only_when_available():
	assert refuse_hold(status=AVAILABLE, code="A-101") is None
	assert "held" in refuse_hold(status=HELD, code="A-101").lower()
	assert "Booked" in refuse_hold(status=BOOKED, code="A-101")
	assert refuse_hold(status=None, code="A-101") == "Unit not found."


def test_second_hold_refused_same_as_unavailable():
	# Concurrent second hold is the same refusal: unit is no longer Available.
	assert refuse_hold(status=HELD, code="A-101") == "Unit A-101 is Held — hold refused."


def test_book_from_available_or_held():
	assert refuse_book(status=AVAILABLE, code="A-101", live_booking=False) is None
	assert refuse_book(status=HELD, code="A-101", live_booking=False) is None
	assert "Sold" in refuse_book(status=SOLD, code="A-101", live_booking=False)
	assert "Dispute" in refuse_book(status=DISPUTE, code="A-101", live_booking=False)


def test_live_booking_includes_possession():
	# Atlas-3 company-day hole: possessed units could be booked again. Closed here.
	assert "already has an active booking" in refuse_book(
		status=BOOKED, code="C-304", live_booking=True
	)


def test_channel_hold_needs_daily_report():
	assert (
		refuse_hold_without_report(roles=["Atlas Channel Agent"], has_today_report=False)
		== "File today’s daily report before placing a hold."
	)
	assert refuse_hold_without_report(roles=["Atlas Channel Agent"], has_today_report=True) is None
	assert refuse_hold_without_report(roles=["Atlas Sales Manager"], has_today_report=False) is None


def test_channel_booking_needs_approval():
	assert channel_needs_booking_approval("Pink City") is True
	assert channel_needs_booking_approval(None) is False
	assert channel_needs_booking_approval("") is False


def test_dispute_is_in_house_overflow():
	assert refuse_dispute(status=AVAILABLE, code="A-101", roles=["Atlas Sales Manager"]) is None
	assert "Channel" in refuse_dispute(status=AVAILABLE, code="A-101", roles=["Atlas Channel Agent"])
	assert "Sold" in refuse_dispute(status=SOLD, code="A-101", roles=["Atlas Sales Manager"])


def test_legal_transitions():
	assert refuse_transition(AVAILABLE, HELD) is None
	assert refuse_transition(HELD, AVAILABLE) is None
	assert refuse_transition(HELD, BOOKED) is None
	assert refuse_transition(BOOKED, SOLD) is None
	assert refuse_transition(BOOKED, AVAILABLE) is None
	assert refuse_transition(HELD, SOLD)
	assert refuse_transition(SOLD, AVAILABLE)
	assert refuse_transition(AVAILABLE, AVAILABLE) is None


def test_expire_due_holds():
	due = holds_due_to_expire(
		[
			{"status": HOLD_HELD, "until": "2026-08-01", "unit": "u1"},
			{"status": HOLD_HELD, "until": "2026-08-24", "unit": "u2"},
			{"status": HOLD_BOOKED, "until": "2026-08-01", "unit": "u3"},
		],
		today="2026-08-24",
	)
	assert [h["unit"] for h in due] == ["u1"]


def test_live_unit_key_enforces_one_live_hold():
	assert live_unit_key(status=HOLD_HELD, unit="AUN-1", hold_name="AHD-9") == "AUN-1"
	assert live_unit_key(status=HOLD_BOOKED, unit="AUN-1", hold_name="AHD-9") == "AHD-9"


def test_hold_expiry_does_not_unlock_a_booked_unit():
	assert unit_status_on_hold_expire(HELD) == AVAILABLE
	assert unit_status_on_hold_expire(BOOKED) is None
	assert unit_status_on_hold_expire(SOLD) is None
	assert unit_status_on_hold_expire(DISPUTE) is None


def test_until_day_is_still_live():
	assert holds_due_to_expire([{"status": HOLD_HELD, "until": "2026-08-24", "unit": "u2"}], today="2026-08-24") == []
