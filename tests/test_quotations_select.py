from erpatlas.quotations.select import award_plan, rank_quotes, refuse_compare, select_winner


def test_compare_needs_quotes_and_ranks_lowest_amount():
	assert "at least one" in refuse_compare([])
	quotes = [
		{"supplier": "B", "amount": "120"},
		{"supplier": "A", "amount": "100"},
	]
	assert select_winner(quotes)["supplier"] == "A"
	assert [q["supplier"] for q in rank_quotes(quotes)] == ["A", "B"]


def test_cannot_award_until_vendor_active():
	quotes = [{"supplier": "A", "amount": "100"}]
	blocked = award_plan(quotes, stages={"A": "Draft"})
	assert "Active" in blocked["error"]
	assert blocked["creates_payment_entry"] is False
	ok = award_plan(quotes, stages={"A": "Active"})
	assert ok.get("next") == "Purchase Order"
	assert ok["winner"]["supplier"] == "A"
	assert ok["creates_payment_entry"] is False
