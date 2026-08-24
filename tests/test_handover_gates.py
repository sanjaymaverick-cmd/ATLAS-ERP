"""Possession waits for Occupancy Certificate, closed snags, and a collected plan."""

from erpatlas.booking.plan import ACTIVE, POSSESSION
from erpatlas.handover.gates import (
	HANDOVER_POSSESSION,
	OC_PENDING,
	OC_RECEIVED,
	possession_effects,
	refuse_possession,
)
from erpatlas.property_inventory.lock import BOOKED, SOLD


def _ok(**overrides):
	base = dict(
		occupancy_certificate=OC_RECEIVED,
		open_snags=0,
		plan_collected="1050000",
		plan_gross="1050000",
		booking_status=ACTIVE,
		unit_status=BOOKED,
	)
	base.update(overrides)
	return refuse_possession(**base)


def test_possession_allowed_when_all_three_gates_pass():
	assert _ok() is None
	assert possession_effects()["unit_to"] == SOLD
	assert possession_effects()["booking_to"] == POSSESSION
	assert possession_effects()["handover_to"] == HANDOVER_POSSESSION


def test_possession_refused_without_occupancy_certificate():
	assert "Occupancy Certificate" in _ok(occupancy_certificate=OC_PENDING)


def test_possession_refused_while_snags_open():
	err = _ok(open_snags=2)
	assert "2 snag" in err
	assert "open" in err


def test_possession_refused_until_plan_collected():
	assert "payment plan" in _ok(plan_collected="1049999", plan_gross="1050000")
	assert _ok(plan_collected="1050000", plan_gross="1050000") is None


def test_possession_only_from_active_booked_unit():
	assert "Active" in _ok(booking_status="Draft")
	assert "already" in _ok(booking_status=POSSESSION, unit_status=SOLD)
	assert "already" in _ok(unit_status=SOLD, booking_status=ACTIVE)
