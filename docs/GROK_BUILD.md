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

Always work in the ATLAS-ERP checkout. Feature work goes on a branch + PR against main. Do not force-push main.

## What this product is

One system: custom Frappe app `erpatlas` on ERPNext version-16. Full Atlas-3 feature parity. Tally is XML migration only; ERPNext Accounts is the books of record. CatBoost stays an external scorer. No separate frontend.

## Load first (every session)

1. CONTEXT.md — words. Challenge a conflicting term immediately.
2. docs/locked-structure.md — modules, roles, invariants. Do not re-open unless the user explicitly changes them.
3. docs/adr/* — especially 0003–0008.
4. docs/modules/property-inventory.md, approvals.md, booking.md, command.md
5. docs/research/README.md — money and isolation contracts.

## Locked stack

- Frappe + ERPNext version-16
- Python >=3.14,<3.15 on the bench
- extend_doctype_class (mixin), never override_doctype_class
- add_to_apps_screen in hooks.py
- required_apps = ["erpnext"]
- Windows bench runs in WSL2, not native Windows Python

## Invariants (never break)

- Unit cannot be held unless Available; concurrent second hold is refused (CAS FOR UPDATE + unique live_unit).
- Commission accrues only. Approvals never create a Payment Entry.
- Possession blocked until snags closed AND OC received AND payment plan collected.
- No PO until vendor is Active (GSTIN).
- Document export is four-eyes + single-use grant.
- Atlas never posts to Tally.
- Channel companies never see each other’s data (query conditions + User Permission on Atlas Channel Company).
- Command AI is read-only: never writes Unit status, PE, or Approvals.

## How to write code

- Prefer native ERPNext objects (Company, Project, Lead, Customer, Sales Order, Payment Entry, Journal Entry, Supplier, Purchase Invoice).
- Custom DocType only when Atlas-3 has logic ERPNext does not provide.
- Put rules in deep modules (property_inventory.lock, approvals.queue, books.payment_gst, booking.plan, command.kpis). Controllers stay thin. Do not import frappe in pure modules.
- Map every field/status/server rule to Atlas-3 acceptance.
- Pure tests: python -m pytest tests -q (must stay green).
- GST/TDS rates are CA configuration, not Python constants.

## Current code on main (as of 2026-08-24, post PR #1 + Booking + Command)

- Property Inventory: Unit / Tower / Hold / Channel Company; lock CAS
- Approvals: unified Atlas Approval queue
- Booking: Atlas Booking + payment steps + Commission Accrued; Active → SO; collect via payment_gst
- books: payment_gst, posting stubs, Sales Order mixin
- Command P0–P2: Desk page; Booking/PE money; deterministic risk cards from Atlas Settings thresholds
- Handover: Occupancy Certificate + snags + full collection → unit Sold / booking Possession
- Channel: Atlas Daily Report gate on hold; Role fixtures
- Commission books: optional accrual JE; Purchase Invoice after Approved; never PE from Approvals
- Commercial: Supplier atlas_stage; GSTIN required; no PO until Active
- Research docs 01–06; docs/modules/command.md, booking.md

## Next implementation slice (unless the user names another)

Prefer one of:

1. Lead & Pipeline (CatBoost stays external)
2. Documents four-eyes export
3. Site diary / inspections
4. Command P3 — daily KPI snapshot / portfolio heat map

Do not implement CatBoost, WhatsApp, Tally import, or RERA 70/30 unless named.

## Language (do not mix)

Legal Entity = ERPNext Company.
Channel Company = agency, custom DocType, not a Company.
Unit = lock. Item is only the SO line (non-stock).
Booking ≠ Sales Order ≠ Payment Entry.
Approval ≠ ERPNext Workflow.

## Git

- Branch from latest main. PR against main.
- Commit messages: what changed and why, Atlas-3 rule if any.
- After code: pytest tests -q must pass.

When the user says “go”, implement the named slice (or the first next item above). If they ask a question, answer from these files first.
```
