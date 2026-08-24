from decimal import Decimal

from erpatlas.books.payment_gst import (
	GST_NONE,
	INCLUSIVE,
	ON_INVOICE,
	ON_RECEIPT,
	books_on_collect,
	expand_schedule,
	invoice_qty,
	money,
	next_unpaid,
	refuse_collect,
	resolve_policy,
	resolve_rate,
	split_gst,
	taxable_gst_gross,
)


def test_inclusive_5_percent_round_trip():
	taxable, gst, gross = taxable_gst_gross(amount="1050000", rate=5, tax_included=INCLUSIVE)
	assert gross == money("1050000")
	assert taxable + gst == gross
	assert gst == money("50000")
	assert taxable == money("1000000")


def test_exclusive_adds_gst():
	taxable, gst, gross = taxable_gst_gross(amount="1000000", rate=5, tax_included="exclusive")
	assert taxable == money("1000000")
	assert gst == money("50000")
	assert gross == money("1050000")


def test_zero_rate_is_passthrough():
	taxable, gst, gross = taxable_gst_gross(amount="500", rate=0, tax_included=INCLUSIVE)
	assert gst == money(0)
	assert taxable == gross == money("500")


def test_intra_state_splits_half_with_residue_on_sgst():
	split = split_gst("0.01", intra_state=True)
	assert split["cgst"] + split["sgst"] == money("0.01")
	assert split["igst"] == money(0)
	split_i = split_gst("50000", intra_state=False)
	assert split_i == {"cgst": money(0), "sgst": money(0), "igst": money("50000")}


def test_policy_defaults_to_gst_on_receipt_until_oc():
	assert resolve_policy(oc_received=False, gst_on_under_construction=True) == ON_RECEIPT
	assert resolve_policy(oc_received=True, gst_on_under_construction=True) == GST_NONE
	assert resolve_policy(oc_received=False, gst_on_under_construction=False) == GST_NONE
	assert resolve_policy(oc_received=False, gst_on_under_construction=True, override=ON_INVOICE) == ON_INVOICE


def test_residential_rates():
	assert resolve_rate(policy=ON_RECEIPT, affordable=False, shop=False) == Decimal("5")
	assert resolve_rate(policy=ON_RECEIPT, affordable=True, shop=False) == Decimal("1")
	assert resolve_rate(policy=GST_NONE, affordable=False, shop=False) == Decimal("0")
	try:
		resolve_rate(policy=ON_RECEIPT, affordable=False, shop=True)
		assert False, "shop must require configured rate"
	except ValueError:
		pass


def test_schedule_percents_and_last_step_absorbs_rounding():
	steps = expand_schedule(
		consideration="1000000",
		rate=5,
		tax_included="exclusive",
		steps=[
			{"label": "Token", "kind": "booking", "percent": "10"},
			{"label": "Slab", "kind": "slab", "percent": "60"},
			{"label": "Possession", "kind": "possession", "percent": "30"},
		],
	)
	assert len(steps) == 3
	assert sum(s["percent"] for s in steps) == money("100")
	assert sum(s["gross"] for s in steps) == money("1050000")
	assert sum(s["taxable"] for s in steps) == money("1000000")
	assert sum(s["gst"] for s in steps) == money("50000")
	assert steps[0]["gross"] == money("105000")
	assert steps[2]["kind"] == "possession"


def test_inclusive_schedule_grand_equals_consideration():
	steps = expand_schedule(
		consideration="1050000",
		rate=5,
		tax_included=INCLUSIVE,
		steps=[{"label": "All", "percent": "100", "kind": "booking"}],
	)
	assert steps[0]["gross"] == money("1050000")
	assert steps[0]["taxable"] == money("1000000")


def test_bad_percent_sum_refused():
	try:
		expand_schedule(
			consideration="100",
			rate=0,
			tax_included=INCLUSIVE,
			steps=[{"percent": "40"}, {"percent": "40"}],
		)
		assert False
	except ValueError as e:
		assert "100" in str(e)


def test_collect_cannot_exceed_step_or_plan():
	assert refuse_collect(
		step_gross="100", already_collected="90", receipt="20", plan_collected="90", plan_gross="200"
	)
	assert refuse_collect(
		step_gross="100", already_collected="0", receipt="100", plan_collected="150", plan_gross="200"
	)
	assert (
		refuse_collect(
			step_gross="100", already_collected="40", receipt="60", plan_collected="40", plan_gross="200"
		)
		is None
	)
	assert refuse_collect(
		step_gross="100", already_collected="0", receipt="0", plan_collected="0", plan_gross="100"
	)


def test_next_unpaid_and_qty_fraction():
	steps = [
		{"idx": 0, "gross": "100", "collected": "100"},
		{"idx": 1, "gross": "200", "collected": "50"},
	]
	nxt = next_unpaid(steps)
	assert nxt and nxt["idx"] == 1
	assert next_unpaid([{**steps[0], "collected": "100"}, {**steps[1], "collected": "200"}]) is None
	assert invoice_qty(step_gross="105000", grand_total="1050000") == Decimal("0.100000")


def test_books_path_follows_policy():
	assert books_on_collect(policy=ON_RECEIPT) == "sales_invoice_then_payment"
	assert books_on_collect(policy=ON_INVOICE) == "payment_against_sales_order"
	assert books_on_collect(policy=GST_NONE) == "payment_against_sales_order"
