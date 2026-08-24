from erpatlas.audit.log import event, refuse_edit
from erpatlas.capital.gates import refuse_amount, refuse_split


def test_loan_and_equity_must_sum_100():
	assert refuse_split(loan_pct="70", equity_pct="30") is None
	assert "100" in refuse_split(loan_pct="70", equity_pct="20")
	assert refuse_amount(amount="0")
	assert refuse_amount(amount="1") is None


def test_audit_is_append_only_and_never_pays():
	assert "append-only" in refuse_edit()
	row = event(actor="md@", action="decided", entity="Atlas Approval", ref="AAP-1")
	assert row["creates_payment_entry"] is False
