# 06 — Payment Schedule GST logic

Pure math: [`erpatlas/books/payment_gst.py`](../../erpatlas/books/payment_gst.py).  
Posting adapter (SO / SI / PE) is not in this slice.

Rates are **Project configuration**. This file is not a CA opinion.

## Locked rules

1. Booking `total_consideration` is the buyer’s cheque total for the unit (one number).
2. `tax_included` on the Project/Booking is `inclusive` or `exclusive`. Default **inclusive** for sales talk (“₹1.05 Cr all-in”).
3. Payment steps are **percents of that consideration, summing to 100**. Last step absorbs rounding so Σ gross = grand total.
4. GST **policy** (not the rate) decides what cash posting looks like:

| Policy | When | On collect |
|---|---|---|
| `on_receipt` | Under-construction residential (no OC). Construction is a **service** — time of supply includes receipt. **Default.** | Sales Invoice for this step, then Payment Entry **against that invoice** |
| `on_invoice` | CA override (treat like goods / delay GST) | Payment Entry against **Sales Order** (advance). SI later allocates |
| `none` | OC already received, or Project `gst_on_under_construction` = 0 | Same as advance PE; tax template empty |

5. After OC is filed, **new** steps use `none`. Already issued GST invoices stay. Do not reverse GST because OC arrived later.
6. Collection cannot exceed the current step or the plan. Possession still needs OC + snags + full collection (Handover).
7. Shop / commercial: rate **must** be set on the Project. Code refuses to invent 12/18.

## Amounts

```
exclusive: taxable = slice_net
           gst     = round(taxable × rate / 100, ₹0.01)
           gross   = taxable + gst

inclusive: gross   = slice_gross
           taxable = round(gross × 100 / (100 + rate), ₹0.01)
           gst     = gross − taxable
```

Intra-state: CGST = round(gst/2), SGST = gst − CGST.  
Inter-state: IGST = gst.

Default residential rate: **5%** (affordable **1%**). Zero when policy is `none`.

SO line: qty 1, net rate = total taxable, taxes template fills GST so **grand_total = Σ step.gross**.

Invoice qty for a step = `step.gross / grand_total` (6 decimal places) so partial SI from the single SO line matches the step.

## Collect algorithm

```
policy = resolve_policy(oc, project.gst_on_under_construction, override)
rate   = resolve_rate(policy, affordable, shop, project.gst_rate)
steps  = expand_schedule(consideration, step percents, rate, tax_included)
step   = next_unpaid(steps)          # first collected < gross
refuse_collect(...)                  # over-step / over-plan / zero
if books_on_collect(policy) == "sales_invoice_then_payment":
    SI qty = invoice_qty(step.gross, grand_total)   # allocate any leftover advance first
    PE against that SI
else:
    PE against SO (advance)
mark step.collected += receipt
```

Never create a Payment Entry from Approvals. Never GST-tax a Hold.

## What ERPNext owns vs Atlas Booking

| Field | Owner |
|---|---|
| label, kind (booking/slab/possession), percent, due_date | Atlas Booking Payment Step |
| taxable, gst, gross, collected, sales_invoice, payment_entry | written by adapter from this math |
| Payment Schedule on SO | generated to match step gross / due_date (not credit-days) |
| Tax template | Project: construction 5%/1% vs nil after OC |

RERA 70/30 bank split is **not** GST. Do not put it here.

## Tests

`python -m pytest tests/test_payment_gst.py tests/test_unit_lock.py tests/test_approvals_queue.py -q`
