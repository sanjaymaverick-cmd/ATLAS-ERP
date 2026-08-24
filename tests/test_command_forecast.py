from erpatlas.command.forecast import MODEL_ID, linear_outlook, narrative_brief
from erpatlas.books.payment_gst import money


def test_linear_outlook_is_advisory_and_named():
	out = linear_outlook(["100", "110", "120"], horizon_days=30)
	assert out["model_id"] == MODEL_ID
	assert out["auto_action"] is False
	assert out["creates_payment_entry"] is False
	assert out["writes_unit"] is False
	assert out["decides_approval"] is False
	assert out["projected"] == money("420")


def test_empty_series_is_zero_not_an_invented_catboost():
	out = linear_outlook([], horizon_days=90)
	assert out["projected"] == money(0)
	assert out["served_by"] == MODEL_ID
	assert "catboost" not in out["served_by"]


def test_narrative_brief_uses_only_structured_json():
	lines = narrative_brief(
		{
			"units": {"Available": 3, "Held": 1, "Booked": 2, "Sold": 0},
			"money": {"booking_value_live": "10", "receivable": "2"},
			"approvals": {"pending": 4, "oldest_days": 9},
			"risk": [{"severity": "red", "title": "2 money Approval(s) past 3 days"}],
		}
	)
	assert any("Available" in x for x in lines)
	assert any("Advisory only" in x for x in lines)
	assert any("Top risk" in x for x in lines)
