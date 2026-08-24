from erpatlas.channel.report import filed_today, refuse_second_report, report_key
from erpatlas.property_inventory.lock import refuse_hold_without_report


def test_one_report_per_agent_per_day():
	assert refuse_second_report(already_filed_today=False) is None
	assert "already filed" in refuse_second_report(already_filed_today=True)
	assert report_key(agent="ag@atlas.local", report_date="2026-08-24") == "ag@atlas.local::2026-08-24"


def test_filed_today_matches_agent_and_date():
	rows = [{"agent": "ag@atlas.local", "report_date": "2026-08-24"}]
	assert filed_today(rows, agent="ag@atlas.local", today="2026-08-24")
	assert not filed_today(rows, agent="ag@atlas.local", today="2026-08-23")
	assert not filed_today(rows, agent="other@atlas.local", today="2026-08-24")


def test_channel_hold_still_needs_today_report():
	assert (
		refuse_hold_without_report(roles=["Atlas Channel Agent"], has_today_report=False)
		== "File today’s daily report before placing a hold."
	)
	assert refuse_hold_without_report(roles=["Atlas Channel Agent"], has_today_report=True) is None
