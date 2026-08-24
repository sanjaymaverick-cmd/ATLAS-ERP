from erpatlas.books.commission import (
	accrual_journal_accounts,
	accrual_journal_lines,
	refuse_payout_invoice,
	refuse_payment_entry_for_commission,
	should_post_accrual_je,
)
from erpatlas.books.payment_gst import money


def test_payout_invoice_only_after_approved_with_supplier():
	assert "Approved" in refuse_payout_invoice(status="Accrued", supplier="SUP-1")
	assert "Supplier" in refuse_payout_invoice(status="Approved", supplier=None)
	assert refuse_payout_invoice(status="Approved", supplier="SUP-1") is None


def test_payment_entry_cannot_target_commission_row():
	assert refuse_payment_entry_for_commission(voucher_type="Atlas Commission", remarks="")
	assert refuse_payment_entry_for_commission(voucher_type="Purchase Invoice", remarks="Atlas Commission ACM-1")
	assert (
		refuse_payment_entry_for_commission(voucher_type="Purchase Invoice", remarks="Agency invoice")
		is None
	)


def test_accrual_je_default_is_on_booking():
	assert should_post_accrual_je(accrue_on="Booking", status="Accrued")
	assert not should_post_accrual_je(accrue_on="Approval", status="Accrued")
	assert should_post_accrual_je(accrue_on="Approval", status="Approved")


def test_journal_lines_balance_and_need_accounts():
	assert accrual_journal_accounts(expense_account=None, payable_account="P")
	lines = accrual_journal_lines(
		amount="20000", expense_account="CE", payable_account="CP", project="Lake"
	)
	assert lines[0]["debit_in_account_currency"] == money("20000")
	assert lines[1]["credit_in_account_currency"] == money("20000")
	assert lines[0]["project"] == "Lake"
