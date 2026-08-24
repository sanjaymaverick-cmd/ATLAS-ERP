# Locked high-level structure

Do not re-open this file unless the user explicitly requests a change. Detail lives in `docs/modules/` and `docs/adr/`.

## Architecture

- One system: a native custom Frappe app (`erpatlas`) on ERPNext.
- ERPNext Accounts is the books of record.
- Tally is migration-only (XML in). Atlas never posts to Tally.
- CatBoost scoring stays an external process (`cat_features`, no Ordered Target Statistics re-implementation).
- Company isolation, hard unit locks, commission accrual, four-eyes, and Atlas-3 cognitive-load UX are preserved.

## Modules

### Group A — Today

- Command (role-adapted home + exception queue)
- Approvals (unified decision queue)
- Portfolio (cross-project open items)

### Group B — Build

- Projects
- Commercial (Vendors & Orders)
- Quotations (RFQ → compare → select → PO)
- Site (Diary + Inspections)
- Controls (Materials)
- Change Control (RFI / NCR / VO)
- Documents (controlled lifecycle + four-eyes export)
- Land & Legal (Parcels, Diligence, Statutory obligations)

### Group C — Sell

- Property Inventory (Towers + Units + hard status lock)
- Channel & Partner (Companies, Agents, Daily Reports, isolation)
- Lead & Pipeline (ingest, dedup, hybrid + CatBoost scoring, Customer 360)
- Booking & Approvals (Hold → Booking + Commission accrual only)
- Handover & Possession (OC, snags, possession gates)
- Communications (WhatsApp template registry)
- Sales Analytics (funnel + model monitor)

### Group D — Books

- Accounts (native ERPNext)
- Capital
- Collections (payment steps under bookings)

### Group E — More

- Organization
- Owner Decisions
- Audit
- Assistant (draft-only)
- Testing (invariant scripts)
- Settings & Integrations

## Roles

- Atlas Developer Admin (`md@` / full access)
- Atlas Project Director
- Atlas Sales Manager
- Atlas Channel Admin (strict Channel Company isolation)
- Atlas Channel Agent
- Atlas Commercial
- Atlas Finance
- Atlas Site
- Atlas Stores
- Atlas Land Legal
- Atlas Documents

Channel seats are isolated by Channel Company via User Permissions plus server query conditions. Isolation is never presentational-only.

## Invariants

- Unit cannot be held unless Available; concurrent second hold is refused.
- Commission accrues only — never auto-pays and never creates a Payment Entry without going through Approvals.
- Possession is blocked until snags are closed and OC is received.
- No PO can be issued until the vendor is Active (GSTIN required).
- Document export is four-eyes + single-use grant.
- Atlas never posts to Tally (Tally only for migration).
- Channel companies never see each other’s data.

## Native vs custom

Prefer ERPNext objects (Company, Project, Lead, Customer, Sales Order, Purchase Order, Journal Entry, Payment Entry, Supplier). Create a custom DocType only when Atlas-3 has domain logic ERPNext does not provide (Unit lock, unified Approval queue, Channel Company, Hold, Export Grant).
