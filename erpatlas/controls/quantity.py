"""Drawing qty vs site measure. No frappe. Not ERPNext stock. Never a Payment Entry."""

from __future__ import annotations

from erpatlas.books.payment_gst import money

PROVISIONAL = "provisional"
VARIANCE = "variance"
APPROVED = "approved"
QUANTITY_STATUSES = (PROVISIONAL, VARIANCE, APPROVED)


def refuse_qty(*, qty) -> str | None:
	if money(qty or 0) < 0:
		return "Quantity cannot be negative."
	return None


def variance_qty(*, drawing_qty, site_qty):
	return money(site_qty or 0) - money(drawing_qty or 0)


def derived_status(*, drawing_qty, site_qty, status: str | None = None) -> str:
	if status == APPROVED:
		return APPROVED
	if money(drawing_qty or 0) == money(site_qty or 0):
		return PROVISIONAL
	return VARIANCE


def refuse_approve(*, status: str | None) -> str | None:
	if status == APPROVED:
		return "This quantity is already approved."
	return None


def refuse_edit_locked(*, status: str | None) -> str | None:
	if status == APPROVED:
		return "Approved quantity is locked."
	return None
