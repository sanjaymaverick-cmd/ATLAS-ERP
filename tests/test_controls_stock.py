from erpatlas.controls.stock import refuse_issue, refuse_receive


def test_cannot_issue_more_than_received():
	assert refuse_receive(qty="1") is None
	assert refuse_receive(qty="0")
	assert refuse_issue(received="10", issued="8", qty="2") is None
	assert "more than accepted" in refuse_issue(received="10", issued="8", qty="3")
