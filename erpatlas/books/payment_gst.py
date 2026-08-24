"""Payment-schedule GST math. No frappe.

Books posting (SO / SI / PE) lives in a later adapter. This module decides
amounts, tax split, next unpaid step, and collection refusals.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Iterable, Mapping

PAISE = Decimal("0.01")

ON_RECEIPT = "on_receipt"
ON_INVOICE = "on_invoice"
GST_NONE = "none"
GST_POLICIES = (ON_RECEIPT, ON_INVOICE, GST_NONE)

INCLUSIVE = "inclusive"
EXCLUSIVE = "exclusive"
TAX_INCLUDED = (INCLUSIVE, EXCLUSIVE)

RESIDENTIAL_STANDARD = Decimal("5")
RESIDENTIAL_AFFORDABLE = Decimal("1")


def money(value) -> Decimal:
	if isinstance(value, Decimal):
		d = value
	else:
		d = Decimal(str(value))
	return d.quantize(PAISE, rounding=ROUND_HALF_UP)


def refuse_rate(rate) -> str | None:
	r = Decimal(str(rate))
	if r < 0 or r > 40:
		return "GST rate is out of range."
	return None


def taxable_gst_gross(*, amount, rate, tax_included: str) -> tuple[Decimal, Decimal, Decimal]:
	"""One slice (a step or the whole booking).

	amount is consideration for that slice: gross if inclusive, net if exclusive.
	"""
	err = refuse_rate(rate)
	if err:
		raise ValueError(err)
	if tax_included not in TAX_INCLUDED:
		raise ValueError("tax_included must be inclusive or exclusive.")
	amt = money(amount)
	r = Decimal(str(rate))
	if r == 0:
		return amt, money(0), amt
	if tax_included == INCLUSIVE:
		taxable = money(amt * Decimal(100) / (Decimal(100) + r))
		gst = money(amt - taxable)
		return taxable, gst, amt
	taxable = amt
	gst = money(amt * r / Decimal(100))
	return taxable, gst, money(taxable + gst)


def split_gst(gst, *, intra_state: bool) -> dict[str, Decimal]:
	g = money(gst)
	if g == 0:
		return {"cgst": money(0), "sgst": money(0), "igst": money(0)}
	if intra_state:
		cgst = money(g / 2)
		sgst = money(g - cgst)
		return {"cgst": cgst, "sgst": sgst, "igst": money(0)}
	return {"cgst": money(0), "sgst": money(0), "igst": g}


def resolve_policy(*, oc_received: bool, gst_on_under_construction: bool, override: str | None = None) -> str:
	if override:
		if override not in GST_POLICIES:
			raise ValueError("Unknown GST policy.")
		return override
	if oc_received or not gst_on_under_construction:
		return GST_NONE
	return ON_RECEIPT


def resolve_rate(*, policy: str, affordable: bool, shop: bool, configured_rate=None) -> Decimal:
	if policy == GST_NONE:
		return Decimal("0")
	if configured_rate is not None:
		err = refuse_rate(configured_rate)
		if err:
			raise ValueError(err)
		return Decimal(str(configured_rate))
	if shop:
		# Commercial under-construction — CA configures; do not invent 12/18 here.
		raise ValueError("Shop GST rate must be set on the Project.")
	return RESIDENTIAL_AFFORDABLE if affordable else RESIDENTIAL_STANDARD


def expand_schedule(
	*,
	consideration,
	steps: Iterable[Mapping],
	rate,
	tax_included: str,
) -> list[dict]:
	"""Percents must sum to 100. Last step absorbs rounding so gross totals match.

	Each input step: label, percent (0-100), optional due_date, optional kind
	(booking | slab | possession).
	"""
	rows = list(steps)
	if not rows:
		raise ValueError("Payment schedule needs at least one step.")
	pct_sum = sum(Decimal(str(s["percent"])) for s in rows)
	if pct_sum != Decimal("100"):
		raise ValueError("Payment step percents must sum to 100.")

	taxable_total, gst_total, gross_total = taxable_gst_gross(
		amount=consideration, rate=rate, tax_included=tax_included
	)

	out: list[dict] = []
	run_taxable = money(0)
	run_gst = money(0)
	run_gross = money(0)
	last = len(rows) - 1
	for i, step in enumerate(rows):
		pct = Decimal(str(step["percent"])) / Decimal("100")
		if i == last:
			taxable = money(taxable_total - run_taxable)
			gst = money(gst_total - run_gst)
			gross = money(gross_total - run_gross)
		else:
			taxable = money(taxable_total * pct)
			gst = money(gst_total * pct)
			gross = money(gross_total * pct)
			run_taxable += taxable
			run_gst += gst
			run_gross += gross
		split = split_gst(gst, intra_state=bool(step.get("intra_state", True)))
		out.append(
			{
				"idx": i,
				"label": step.get("label") or f"Step {i + 1}",
				"kind": step.get("kind") or "slab",
				"percent": money(step["percent"]),
				"due_date": step.get("due_date"),
				"taxable": taxable,
				"gst": gst,
				"gross": gross,
				**split,
			}
		)
	return out


def invoice_qty(*, step_gross, grand_total) -> Decimal:
	"""Fraction of the single SO line (qty 1) to bill for this step."""
	g = money(grand_total)
	if g == 0:
		raise ValueError("Grand total is zero.")
	return (money(step_gross) / g).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)


def refuse_collect(
	*,
	step_gross,
	already_collected,
	receipt,
	plan_collected,
	plan_gross,
) -> str | None:
	r = money(receipt)
	if r <= 0:
		return "Collection must be greater than zero."
	step_left = money(step_gross) - money(already_collected)
	if r > step_left:
		return "Collection cannot exceed this payment step."
	if money(plan_collected) + r > money(plan_gross):
		return "Collection cannot exceed the payment plan."
	return None


def next_unpaid(steps: Iterable[Mapping]) -> dict | None:
	"""First step whose collected < gross. Order is idx."""
	ordered = sorted(steps, key=lambda s: int(s.get("idx", 0)))
	for step in ordered:
		if money(step.get("collected") or 0) < money(step["gross"]):
			return dict(step)
	return None


def books_on_collect(*, policy: str) -> str:
	"""What the adapter must post when cash is taken."""
	if policy == ON_RECEIPT:
		return "sales_invoice_then_payment"
	if policy == ON_INVOICE:
		return "payment_against_sales_order"
	return "payment_against_sales_order"
