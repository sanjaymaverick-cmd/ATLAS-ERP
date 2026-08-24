# Booking — DocType design

**Atlas-3 sources:** `src/lib/types.ts` `Booking` / `PaymentStep` / `Commission`, `src/lib/store.ts` (`addBooking`, `bookHold`, `collect`, `accrueCommission`).

**Contracts:** [research/02](../research/02-booking-sales-order-gst.md), [research/06](../research/06-payment-schedule-gst.md), [research/03](../research/03-commission-tds.md), ADR 0007.

**ERPNext:** Sales Order (created on Active), Sales Invoice + Payment Entry (on collect). Unit stays the lock. Item is only the SO line (non-stock `ATLAS-UNIT`).

## Acceptance (must remain true)

| Atlas-3 criterion | ERPATLAS rule |
|---|---|
| Booking is not a Sales Order | Atlas Booking owns unit, partner, steps, commission trigger |
| Hold never creates an SO | Only Booking **Active** submits the SO |
| In-house `bookHold` books immediately | `request_booking` → `activate_from_hold` |
| Channel hold → booking waits in Approvals | Approval kind `Hold booking`; unit stays Held |
| On book: unit Booked, hold Booked | CAS Held → Booked, then close Hold |
| Commission accrues, never auto-pays | `Atlas Commission` status Accrued; no Payment Entry |
| Percents sum to 100 | `refuse_step_percents` / `expand_schedule` |
| Collection cannot exceed the plan | `refuse_collect` / `refuse_collect_booking` |
| GST on receipt default | `on_receipt` → SI for the step, then PE against SI |
| Channel isolation | Query conditions; Channel may read units they held or booked |
| Cancel before possession | SO cancel if no money; unit → Available. Possession cannot cancel |

Handover / Possession is a separate module. Not here: CatBoost, WhatsApp, Tally, RERA 70/30, commission JE / TDS PI.

## DocTypes

### Atlas Booking

| Field | Type | Notes |
|---|---|---|
| naming_series | Data | `ABK-.#####` |
| project | Link → Project | Copied from unit |
| company | Link → Company | Legal Entity from Project |
| unit | Link → Atlas Unit | The lock |
| hold | Link → Atlas Unit Hold | Empty if booked from Available |
| customer | Link → Customer | Created from hold `customer_name` if needed |
| customer_name | Data | |
| channel_company | Link → Atlas Channel Company | Empty = in-house |
| agent | Link → User | |
| total_consideration | Currency | Buyer cheque total |
| collected | Currency | Sum of step collections |
| tax_included | Select | inclusive (default) / exclusive |
| gst_policy | Select | Resolved on Active: on_receipt / on_invoice / none |
| gst_rate | Percent | Resolved on Active; CA config on Project |
| status | Select | Draft / Active / Cancelled / Possession |
| sales_order | Link → Sales Order | Submitted on Active |
| commission | Link → Atlas Commission | Accrued if channel Active |
| live_unit | Data | Unique: unit name while Active/Possession |
| payment_steps | Table → Atlas Booking Payment Step | Percents sum to 100 |

### Atlas Booking Payment Step (child)

label, kind (`booking` / `slab` / `possession`), percent, due_date. On Active: taxable, gst, cgst, sgst, igst, gross. On collect: collected, sales_invoice, payment_entry.

Default when none given: one step **Consideration** 100% kind `booking`.

### Atlas Commission

booking (unique), channel_company, project, amount (`consideration × rate / 100`), status Accrued / Approved / Rejected / Paid. Approval kind `Commission` flips Approved/Rejected. **Never a Payment Entry.**

## Status machine — Booking

```
Draft ──activate──► Active ──cancel──► Cancelled   (unit → Available; no posted money)
                      │
                      └── (Handover later) ──► Possession
```

Direct form edits of `status` are refused unless `frappe.flags.in_atlas_booking`.

## Server rules

1. `activate_booking` / `activate_from_hold` — `refuse_activate`; `expand_schedule`; CAS unit → Booked; close Hold; submit SO (`atlas_booking` / `atlas_unit`); accrue Commission.
2. SO line: qty 1, non-stock Item `ATLAS-UNIT`. Rate = taxable if a Project tax template is set, else grand (inclusive cash total) so payment schedule sums.
3. `collect` — `next_unpaid` + `refuse_collect`; Channel seats refused. Raises Approval kind **Payment** (Finance Lead). Payment Entry is created only on Approved (`post_collect`). `on_receipt` → SI then PE against SI; `on_invoice` / `none` → PE against SO.
4. `cancel` — refused if Possession / Sold / posted money.
5. Channel `request_booking` still raises Approval kind `Hold booking`. Handler calls `activate_from_hold` (does **not** CAS the unit by itself).

## Whitelist

- `erpatlas.booking.doctype.atlas_booking.atlas_booking.activate`
- `erpatlas.booking.doctype.atlas_booking.atlas_booking.collect`
- `erpatlas.booking.doctype.atlas_booking.atlas_booking.cancel`
- `erpatlas.booking.doctype.atlas_commission.atlas_commission.send_to_approvals`
- `erpatlas.property_inventory.doctype.atlas_unit_hold.atlas_unit_hold.request_booking` (unchanged path, now creates a Booking)

## Out of this slice

Handover (OC, snags, Possession), booking KYC documents, commission Journal Entry / Purchase Invoice / TDS, RERA 70/30.
