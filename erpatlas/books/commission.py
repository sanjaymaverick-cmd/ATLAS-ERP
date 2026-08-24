"""Commission books rules. No frappe. Never a Payment Entry from Approvals."""

from __future__ import annotations

from erpatlas.booking.plan import COMMISSION_ACCRUED, COMMISSION_APPROVED
from erpatlas.books.payment_gst import money

ACCRUE_ON_BOOKING = "Booking"
ACCRUE_ON_APPROVAL = "Approval"


def refuse_payout_invoice(*, status: str, supplier: str | None) -> str | None:
	if status != COMMISSION_APPROVED:
		return "Commission must be Approved before a Purchase Invoice."
	if not supplier:
		return "Channel Company needs a Supplier before commission can be invoiced."
	return None


def refuse_payment_entry_for_commission(*, voucher_type: str | None, remarks: str | None) -> str | None:
	if voucher_type == "Atlas Commission":
		return "Commission is accrued only. Pay the Purchase Invoice, not the Commission row."
	blob = (remarks or "").lower()
	if "atlas commission" in blob:
		return "Commission is accrued only. Pay the Purchase Invoice, not the Commission row."
	return None


def should_post_accrual_je(*, accrue_on: str, status: str) -> bool:
	if accrue_on == ACCRUE_ON_APPROVAL:
		return status == COMMISSION_APPROVED
	return status == COMMISSION_ACCRUED


def accrual_journal_accounts(*, expense_account: str | None, payable_account: str | None) -> str | None:
	if not expense_account or not payable_account:
		return "Set commission expense and payable accounts on Atlas Settings before posting an accrual journal."
	return None


def accrual_journal_lines(*, amount, expense_account: str, payable_account: str, project: str | None) -> list[dict]:
	amt = money(amount)
	return [
		{"account": expense_account, "debit_in_account_currency": amt, "credit_in_account_currency": money(0), "project": project},
		{"account": payable_account, "debit_in_account_currency": money(0), "credit_in_account_currency": amt, "project": project},
	]
