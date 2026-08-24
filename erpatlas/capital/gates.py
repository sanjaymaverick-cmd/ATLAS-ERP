"""Funding sanction rules. No frappe. Loan + equity must be 100."""

from __future__ import annotations

from erpatlas.books.payment_gst import money

STATUSES = ("draft", "sanctioned", "disbursing", "closed")


def refuse_split(*, loan_pct, equity_pct) -> str | None:
	total = money(loan_pct or 0) + money(equity_pct or 0)
	if total != money(100):
		return "Loan percent and equity percent must sum to 100."
	return None


def refuse_amount(*, amount) -> str | None:
	if money(amount or 0) <= 0:
		return "Sanction amount must be greater than zero."
	return None
