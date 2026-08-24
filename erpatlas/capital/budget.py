"""Project cost-code budget vs committed. No frappe. Not a voucher."""

from __future__ import annotations

from erpatlas.books.payment_gst import money


def refuse_amounts(*, budget, committed) -> str | None:
	if money(budget or 0) < 0:
		return "Budget cannot be negative."
	if money(committed or 0) < 0:
		return "Committed cannot be negative."
	return None


def remaining(*, budget, committed):
	return money(budget or 0) - money(committed or 0)
