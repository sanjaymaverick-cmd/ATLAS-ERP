# Grok Build / CLI — ERPATLAS continuity prompt

Copy everything inside the fenced block below into a new Grok Build (or CLI) session. Do not summarise it away.

```text
# ERPATLAS — Grok Build / CLI brief

You are continuing ERPATLAS. This is a native Frappe app on ERPNext, not a TanStack/web-preview app. Do not scaffold a Vite/React site. Do not serve :8080 unless the user explicitly asks for a throwaway mock.

## Paths

- GitHub: https://github.com/sanjaymaverick-cmd/ATLAS-ERP
- Local (Windows): D:\work Dir\Atlas-ERP
- Atlas-3 product source (behaviour only, not the runtime): https://github.com/sanjaymaverick-cmd/Atlas-3  and  D:\work Dir\Atlas 3
- App package name: erpatlas
- Bench install: bench get-app erpatlas "D:\work Dir\Atlas-ERP" then bench --site SITE install-app erpatlas

Always work in the ATLAS-ERP checkout. Feature work goes on a branch + PR against main (first commit b187475 was the empty-repo exception).

## What this product is

One system: custom Frappe app `erpatlas` on ERPNext version-16. Full Atlas-3 feature parity. Tally is XML migration only; ERPNext Accounts is the books of record. CatBoost stays an external scorer. No separate frontend.

## Load first (every session)

1. CONTEXT.md — words. Challenge a conflicting term immediately.
2. docs/locked-structure.md — modules, roles, invariants. Do not re-open unless the user explicitly changes them.
3. docs/adr/* — especially 0003 unified approvals, 0004 unit is the lock, 0005 three company words, 0006 MD four-eyes bypass ON, 0007 booking then Sales Order, 0008 ERPNext v16.
4. docs/modules/property-inventory.md and docs/modules/approvals.md
5. docs/research/README.md — money and isolation contracts.

## Locked stack

- Frappe + ERPNext version-16
- Python >=3.14,<3.15 on the bench
- extend_doctype_class (mixin), never override_doctype_class
- add_to_apps_screen in hooks.py
- required_apps = ["erpnext"]
- Windows bench runs in WSL2, not native Windows Python

## Invariants (never break)

- Unit cannot be held unless Available; concurrent second hold is refused (CAS FOR UPDATE in lock_adapter + unique live_unit).
- Commission accrues only. Approvals never create a Payment Entry.
- Possession blocked until snags closed AND OC received AND payment plan collected.
- No PO until vendor is Active (GSTIN).
- Document export is four-eyes + single-use grant.
- Atlas never posts to Tally.
- Channel companies never see each other’s data (permission_query_conditions + User Permission on Atlas Channel Company, not ERPNext Company).

## How to write code

- Prefer native ERPNext objects (Company, Project, Lead, Customer, Sales Order, Payment Entry, Journal Entry, Supplier, Purchase Invoice).
- Custom DocType only when Atlas-3 has logic ERPNext does not provide.
- Put rules in deep modules (property_inventory.lock, approvals.queue, books.payment_gst). Controllers stay thin. Do not import frappe in lock.py / payment_gst.py.
- Map every field/status/server rule to Atlas-3 acceptance.
- Pure tests: python -m pytest tests -q  (must stay green; they do not need a site).
- GST/TDS rates are CA configuration, not Python constants.

## Current code (as of 2026-08-24)

main: b187475 scaffold — Atlas Unit / Tower / Hold / Channel Company / Atlas Approval / lock CAS / unified queue.

Branch research/money-isolation-v16 (PR https://github.com/sanjaymaverick-cmd/ATLAS-ERP/pull/1) also has:
- ADR 0008 + docs/research/01–06
- erpatlas/books/payment_gst.py (GST on-receipt default, inclusive/exclusive, last-step rounding)
- hooks add_to_apps_screen + empty extend_doctype_class
- pyproject requires-python 3.14

If that PR is not merged, checkout or rebase it before Booking work.

## Next implementation slice (unless the user names another)

Atlas Booking, following docs/research/02 and docs/research/06:

1. Custom Atlas Booking DocType + payment-step child table (labels, percents summing to 100).
2. On Active: CAS unit → Booked, close Hold, create submitted Sales Order (non-stock Item, custom atlas_booking / atlas_unit), expand_schedule GST math, accrue Commission (status Accrued, no PE).
3. Collect: next_unpaid + refuse_collect; on_receipt → Sales Invoice for the step then PE against SI; on_invoice / none → PE against SO.
4. Channel hold→book still goes through Approval kind Hold booking (already wired).
5. Isolation: Channel may read units they held or booked (see research/05 gap).
6. Do not implement Handover, CatBoost, WhatsApp, Tally import, or RERA 70/30 in this slice.

## Language (do not mix)

Legal Entity = ERPNext Company.
Channel Company = agency, custom DocType, not a Company.
Unit = lock. Item is only the SO line (non-stock).
Booking ≠ Sales Order ≠ Payment Entry.
Approval ≠ ERPNext Workflow.

## Git

- Do not force-push main.
- Commit messages: what changed and why, Atlas-3 rule if any.
- After code: pytest tests -q must pass.

When the user says “go”, start Atlas Booking from the contracts above. If they ask a question, answer from these files first.
```
