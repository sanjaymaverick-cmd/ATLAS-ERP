from erpatlas.command.boardpack import DISCLAIMER, feature_summary, render_boardpack
from erpatlas.command.forecast import MODEL_ID


def _board():
	return {
		"filters": {"company": "Atlas Dev", "project": "Lake"},
		"units": {"Available": 3, "Held": 1, "Booked": 2, "Sold": 0},
		"holds": {"held": 1, "expiring_soon": 1},
		"approvals": {"pending": 4, "past_sla": 1, "oldest_days": 9, "sla_days": 3},
		"exceptions": [
			{
				"name": "AAP-3",
				"kind": "Commission",
				"title": "Pay <script>alert(1)</script>",
				"waiting_on": "Atlas Finance",
				"aging_days": 9,
				"project": "Lake",
			}
		],
		"money": {
			"booking_value_live": "10.00",
			"booking_value_mtd": "4.00",
			"collections_mtd": "1.00",
			"plan_gross": "10.00",
			"plan_collected": "8.00",
			"receivable": "2.00",
			"commission_liability": "0.50",
			"hold_conversion_pct": "50.00",
			"channel_bookings": 1,
			"in_house_bookings": 1,
		},
		"shows_money": True,
		"risk": [
			{
				"domain": "approval stall",
				"severity": "red",
				"title": "2 money Approval(s) past 3 days",
				"driver": "Oldest 9d",
				"waiting_on": "Atlas Finance",
			}
		],
		"portfolio": [{"project": "Lake", "health": "amber", "drivers": ["diary gap 4d"]}],
		"sparkline": ["10.00", "11.00"],
		"outlook_30": {
			"projected": "420.00",
			"model_id": MODEL_ID,
			"auto_action": False,
		},
		"outlook_90": {"projected": "1110.00", "model_id": MODEL_ID},
		"brief": ["Inventory: 3 Available.", "Advisory only — Command does not approve, pay, or change a unit."],
	}


def test_pack_is_advisory_and_stores_as_of_and_model():
	pack = render_boardpack(_board(), as_of="2026-08-24")
	assert pack["as_of"] == "2026-08-24"
	assert pack["model_id"] == MODEL_ID
	assert pack["served_by"] == MODEL_ID
	assert "catboost" not in pack["served_by"]
	assert pack["auto_action"] is False
	assert pack["writes_unit"] is False
	assert pack["creates_payment_entry"] is False
	assert pack["decides_approval"] is False
	assert pack["filename"] == "command-boardpack-2026-08-24.pdf"
	summary = pack["feature_summary"]
	assert summary["available"] == 3
	assert summary["pending_approvals"] == 4
	assert summary["model_id"] == MODEL_ID
	assert summary == feature_summary(_board())


def test_html_is_the_command_json_not_a_write():
	html = render_boardpack(_board(), as_of="2026-08-24")["html"]
	assert "Command board pack" in html
	assert "2026-08-24" in html
	assert "Atlas Dev" in html
	assert "Lake" in html
	assert "Waiting for a yes" in html
	assert "linear-snapshot" in html
	assert "Not CatBoost" in html
	assert "Pay &lt;script&gt;alert(1)&lt;/script&gt;" in html
	assert "<script>alert(1)</script>" not in html
	assert "420.00" in html
	assert "2 money Approval(s) past 3 days" in html
	assert DISCLAIMER.split("—")[0].strip() in html
	assert "does not approve" in html


def test_empty_board_still_prints_and_never_acts():
	pack = render_boardpack({}, as_of="2026-08-01")
	assert pack["auto_action"] is False
	assert pack["model_id"] == MODEL_ID
	assert "No pending Approvals" in pack["html"]
	assert "No risk cards" in pack["html"]
	assert pack["feature_summary"]["risk_count"] == 0
