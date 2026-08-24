"""Land instalment reminder. Ops status only — never a Payment Entry, never Tally."""

from __future__ import annotations

from erpatlas.books.payment_gst import money

DUE = "due"
PAID = "paid"
INSTALMENT_STATUSES = (DUE, PAID)


def refuse_pay(*, status: str | None, amount) -> str | None:
	if status == PAID:
		return "Already paid."
	if money(amount or 0) <= 0:
		return "Instalment amount must be greater than zero."
	return None


def pay_effects() -> dict:
	return {
		"status": PAID,
		"creates_payment_entry": False,
		"posts_to_tally": False,
	}
