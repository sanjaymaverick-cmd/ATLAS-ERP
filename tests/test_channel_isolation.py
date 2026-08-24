"""Channel Company isolation — research/05. Pink City never sees Desert Reach."""

from erpatlas.booking.plan import channel_may_read_unit
from erpatlas.property_inventory.lock import AVAILABLE, BOOKED, HELD, SOLD
from erpatlas.property_inventory.permissions import (
	booking_query_clause,
	unit_query_clause,
)


def test_channel_sees_available_and_own_held_or_booked_units():
	assert channel_may_read_unit(status=AVAILABLE, own_hold=False, own_booking=False)
	assert channel_may_read_unit(status=HELD, own_hold=True, own_booking=False)
	assert channel_may_read_unit(status=BOOKED, own_hold=False, own_booking=True)
	assert channel_may_read_unit(status=BOOKED, own_hold=True, own_booking=False)
	assert channel_may_read_unit(status=SOLD, own_hold=False, own_booking=True)


def test_channel_does_not_see_another_firm_booked_unit():
	assert not channel_may_read_unit(status=HELD, own_hold=False, own_booking=False)
	assert not channel_may_read_unit(status=BOOKED, own_hold=False, own_booking=False)
	assert not channel_may_read_unit(status=SOLD, own_hold=False, own_booking=False)


def test_unit_query_includes_own_hold_or_booking_not_only_held():
	sql = unit_query_clause("'Pink City'")
	assert "Available" in sql
	assert "tabAtlas Unit Hold" in sql
	assert "tabAtlas Booking" in sql
	assert "Active" in sql
	assert "Possession" in sql
	# Booked holds still grant visibility — do not require hold status Held only.
	assert "h.status = 'Held'" not in sql


def test_unit_query_without_company_is_available_only():
	sql = unit_query_clause(None)
	assert "Available" in sql
	assert "tabAtlas Booking" not in sql


def test_booking_query_is_own_channel_company():
	sql = booking_query_clause("'Pink City'")
	assert "channel_company" in sql
	assert "Pink City" in sql
	assert booking_query_clause(None) == "1=0"
