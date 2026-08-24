from erpatlas.analytics.funnel import build_sales_analytics, funnel_counts, model_monitor
from erpatlas.books.cases import EXCEPTION, RECONCILED, refuse_settle, settle_effects
from erpatlas.books.payment_gst import money
from erpatlas.capital.budget import refuse_amounts, remaining
from erpatlas.documents.drawing import refuse_register
from erpatlas.land.instalment import PAID, refuse_pay
from erpatlas.pipeline.customer import customer_file


def test_instalment_pay_is_ops_only():
	assert refuse_pay(status=PAID, amount="10")
	assert refuse_pay(status="due", amount="0")
	assert refuse_pay(status="due", amount="10") is None


def test_drawing_needs_title_and_has_no_viewer():
	assert refuse_register(title="")
	assert refuse_register(title="Tower B raft") is None


def test_budget_remaining():
	assert remaining(budget="100", committed="25") == money("75")
	assert refuse_amounts(budget="-1", committed="0")
	assert refuse_amounts(budget="10", committed="2") is None


def test_books_case_never_posts():
	assert "written acceptance" in refuse_settle(status="open", decision=EXCEPTION, note="")
	assert refuse_settle(status="open", decision=RECONCILED, note=None) is None
	effects = settle_effects(RECONCILED)
	assert effects["creates_payment_entry"] is False
	assert effects["posts_to_tally"] is False
	assert refuse_settle(status=RECONCILED, decision=EXCEPTION, note="ok")


def test_funnel_and_monitor_do_not_run_catboost():
	leads = [
		{"atlas_stage": "inquiry", "atlas_band": "hot", "atlas_score_model": "hybrid"},
		{"atlas_stage": "won", "atlas_band": "warm", "atlas_score_model": "catboost"},
		{"atlas_stage": "lost", "atlas_band": "cool", "atlas_score_model": "hybrid"},
	]
	counts = {row["stage"]: row["count"] for row in funnel_counts(leads)}
	assert counts["inquiry"] == 1
	assert counts["won"] == 1
	board = build_sales_analytics(leads)
	assert board["conversion_pct"] == 50
	assert board["creates_payment_entry"] is False
	mon = model_monitor(leads)
	assert mon["hybrid"] == 2
	assert mon["external_catboost"] == 1
	assert mon["reimplements_catboost"] is False


def test_customer_file_is_read_only():
	row = customer_file(
		phone=" 98765 ",
		leads=[{"name": "CRM-1"}],
		bookings=[{"name": "ABK-1"}],
		commissions=[{"status": "Accrued"}],
	)
	assert row["phone"] == "98765"
	assert row["creates_payment_entry"] is False
	assert row["writes_unit"] is False
	assert len(row["leads"]) == 1
