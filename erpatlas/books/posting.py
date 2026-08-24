"""SO / SI / PE payload builders. No frappe.

The adapter that inserts and submits lives in booking.activate / booking.collect.
"""

from __future__ import annotations

from typing import Iterable, Mapping

from erpatlas.books.payment_gst import books_on_collect, invoice_qty, money


def sales_order_payload(
	*,
	customer: str,
	company: str,
	project: str,
	item_code: str,
	unit_code: str,
	booking: str,
	unit: str,
	taxable_total,
	steps: Iterable[Mapping],
	transaction_date: str,
	delivery_date: str,
) -> dict:
	return {
		"doctype": "Sales Order",
		"customer": customer,
		"company": company,
		"project": project,
		"transaction_date": transaction_date,
		"delivery_date": delivery_date,
		"atlas_booking": booking,
		"atlas_unit": unit,
		"items": [
			{
				"item_code": item_code,
				"qty": 1,
				"rate": float(money(taxable_total)),
				"description": unit_code,
				"delivery_date": delivery_date,
			}
		],
		"payment_schedule": [
			{
				"due_date": step.get("due_date") or delivery_date,
				"invoice_portion": float(step["percent"]),
				"payment_amount": float(step["gross"]),
			}
			for step in steps
		],
	}


def collect_posting(*, policy: str, receipt, grand_total, sales_order: str) -> dict:
	path = books_on_collect(policy=policy)
	if path == "sales_invoice_then_payment":
		return {
			"path": path,
			"against": "Sales Invoice",
			"invoice_qty": invoice_qty(step_gross=receipt, grand_total=grand_total),
			"amount": money(receipt),
		}
	return {
		"path": path,
		"against": "Sales Order",
		"reference": sales_order,
		"amount": money(receipt),
	}


def payment_entry_payload(
	*,
	company: str,
	customer: str,
	amount,
	against_doctype: str,
	against_name: str,
	booking: str,
	mode_of_payment: str | None,
	paid_from: str,
	paid_to: str,
	posting_date: str,
) -> dict:
	amt = float(money(amount))
	row = {
		"doctype": "Payment Entry",
		"payment_type": "Receive",
		"company": company,
		"party_type": "Customer",
		"party": customer,
		"paid_from": paid_from,
		"paid_to": paid_to,
		"paid_amount": amt,
		"received_amount": amt,
		"posting_date": posting_date,
		"atlas_booking": booking,
		"references": [
			{
				"reference_doctype": against_doctype,
				"reference_name": against_name,
				"allocated_amount": amt,
			}
		],
	}
	if mode_of_payment:
		row["mode_of_payment"] = mode_of_payment
	return row
