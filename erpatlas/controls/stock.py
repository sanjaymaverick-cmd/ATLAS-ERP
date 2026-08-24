"""Material issue vs receipt. No frappe."""

from __future__ import annotations

from erpatlas.books.payment_gst import money


def refuse_receive(*, qty) -> str | None:
	if money(qty) <= 0:
		return "Receipt quantity must be greater than zero."
	return None


def refuse_issue(*, received, issued, qty) -> str | None:
	if money(qty) <= 0:
		return "Issue quantity must be greater than zero."
	if money(issued) + money(qty) > money(received):
		return "Cannot issue more than accepted receipts."
	return None
