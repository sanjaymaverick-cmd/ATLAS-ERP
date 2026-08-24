# 02 — Booking ↔ Sales Order ↔ Payment Schedule + GST / advances

Atlas-3 Booking is operational (unit lock, partner, payment steps, handover, commission). ERPNext Accounts is the books. This note is the money contract.

**Locked already:** ADR 0007 — Booking is not a Sales Order. A Hold never creates a Sales Order. Approving commission never creates a Payment Entry.

## Objects

| Object | System of record | Job |
|---|---|---|
| **Atlas Booking** (custom, not yet in repo) | ERPATLAS | One unit, one Customer, payment *plan*, possession gates, commission accrual trigger, handover case |
| **Sales Order** | ERPNext Selling | Customer + amount + taxes + Payment Schedule. Created when Booking becomes **Active** |
| **Payment Entry** | ERPNext Accounts | Cash in. Against Customer, linked to Sales Order (advance) then allocated to Sales Invoice |
| **Sales Invoice** | ERPNext Accounts | Revenue recognition / GST tax invoice. Raised on demand / milestone — **not** at hold, **not** at possession by default |
| **Item** | ERPNext Stock | Non-stock Item representing the sold unit (or unit type). Warehouse stock is **not** used. Atlas Unit remains the lock |

Do not treat Atlas Unit as an ERPNext Item. Create (or reuse) a **non-stock** Item so Sales Order has a row. Link `Atlas Booking.unit` on a custom field of the Sales Order.

## Lifecycle

```
Hold (unit Held)
  → (channel) Atlas Approval kind Hold booking
  → Atlas Booking status Active
       ├─ CAS: Unit Held/Available → Booked
       ├─ close Hold → Booked
       ├─ create Sales Order (draft→submit) for same Customer, company, amount
       ├─ apply Payment Terms Template → Payment Schedule
       └─ create Atlas Commission Accrued (see 03)
Collect against next unpaid step
  → Payment Entry (Receive) against Customer + Sales Order  (advance)
Demand / milestone invoice
  → Sales Invoice from Sales Order, allocate advances
Possession (OC + snags closed + plan collected)
  → Unit Booked → Sold
  → Booking Possession
Cancel (before possession)
  → cancel/amend SO if no posted invoices; refund via Payment Entry
  → Unit → Available
```

## Payment Schedule vs Atlas payment steps

Atlas-3 lists labelled steps under the booking (booking amount, slab, possession). ERPNext **Payment Terms Template** generates a **Payment Schedule** on the Sales Order (percent + due date).

**Contract:**

1. Atlas Booking owns the **labels and gates** (which step is “booking token”, which is “possession”). Child table `Atlas Booking Payment Step`: `label`, `percent` or `amount`, `due_date`, `collected`, `sales_invoice` (optional).
2. On Booking Active, ERPATLAS builds or selects a **Payment Terms Template** (project default, or a one-off schedule written onto the SO).
3. Percents on Booking steps **must sum to 100% of total_consideration** (same as ERPNext template rule).
4. Collection UI posts a **Payment Entry** for `min(remaining_on_step, unallocated_needed)`, party = Customer, references = Sales Order. Then marks the step collected.
5. Over-collection is refused (Atlas-3: collection cannot exceed plan).
6. Possession is blocked until every step is collected **and** OC + snags (Handover). Books do not decide possession.

Due dates: prefer explicit dates on Booking steps (construction milestones). Payment Terms “credit days from posting date” is a fallback, not the primary model for real estate.

## GST (India, residential — confirm with CA)

Research snapshot 2026, **not legal advice**:

| Situation | Typical GST | Implication for ERPATLAS |
|---|---|---|
| Under-construction residential (no OC) | 5% without ITC (1% affordable if criteria met) | Sales Invoice / tax template on the SO must carry this rate while OC is not received |
| Ready-to-move after OC | GST generally not on sale of completed immovable property | Switch tax template; stamp duty is outside ERPNext GST |
| Commercial / shop | Different (often 18% with ITC — confirm) | Unit.kind `Shop` uses a different tax category |
| Land | Often excluded / deemed; current 5% composition-style is usually on consideration | Do not invent a land split in code; put it in the tax template |

**GST posting and step math:** locked in [06 — Payment Schedule GST logic](06-payment-schedule-gst.md). Default under-construction: **GST on receipt** (Sales Invoice then Payment Entry). Naked SO advance is the CA override / post-OC path.


Flag on Project: `gst_on_under_construction` (Check). When OC is filed on Handover, stop using the construction GST template for remaining invoices.

RERA 70/30 collection account is **out of this note** (separate module). Do not mix it into GST.

## Sales Order field map (minimum)

Custom fields on Sales Order (fixtures + `extend_doctype_class`):

| Field | Type | Rule |
|---|---|---|
| `atlas_booking` | Link → Atlas Booking | Unique. One live SO per Active booking |
| `atlas_unit` | Link → Atlas Unit | Fetch from booking |

SO items: one row, non-stock Item, qty 1, rate = booking consideration (ex-tax or inclusive — match the tax template).

SO cannot be submitted if `atlas_booking` is missing when created by ERPATLAS. Manual SO without a booking is allowed for non-unit work; do not lock native Selling.

Cancel Booking:

1. If SO has no submitted Sales Invoice and no Payment Entry: cancel SO, Booking → Cancelled, Unit → Available.
2. If money exists: Finance path only — credit note / refund Payment Entry, then cancel. Possession bookings cannot cancel (unit Sold).

## What we will not do

- Create SO on Hold.
- Use Delivery Note / warehouse qty for a flat.
- Let Payment Entry appear from Approvals.
- Treat Payment Schedule percents as possession permission (Handover still owns OC + snags).
