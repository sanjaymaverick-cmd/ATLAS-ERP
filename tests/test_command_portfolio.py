from erpatlas.command.portfolio import AMBER, GREEN, RED, heat_map, project_health, sparkline
from erpatlas.books.payment_gst import money


def test_health_red_on_open_ncr_or_approval_pile():
	assert project_health(open_ncrs=1)["health"] == RED
	assert project_health(pending_approvals=3)["health"] == RED
	assert project_health()["health"] == GREEN
	assert project_health()["auto_action"] is False


def test_health_amber_on_diary_gap_or_collection_lag():
	assert project_health(diary_gap_days=3)["health"] == AMBER
	assert project_health(receivable_pct=25)["health"] == AMBER


def test_heat_map_sorts_red_first_and_never_acts():
	rows = heat_map(
		[
			{"project": "Quiet", "diary_gap_days": 4},
			{"project": "Broken", "open_ncrs": 2},
			{"project": "Fine"},
		]
	)
	assert [r["project"] for r in rows] == ["Broken", "Quiet", "Fine"]
	assert rows[0]["health"] == RED
	assert all(r["auto_action"] is False for r in rows)


def test_sparkline_keeps_money_points():
	assert sparkline(["10", "20", "15"]) == [money("10"), money("20"), money("15")]
	assert sparkline([]) == []
