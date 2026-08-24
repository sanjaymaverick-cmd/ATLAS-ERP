# Grok Build / CLI — Command (CEO dashboard) prompt

Copy everything inside the fenced block into a Grok Build or CLI session after the base ERPATLAS brief (`docs/GROK_BUILD.md`).

```text
# ERPATLAS — Command (CEO dashboard) slice

You are implementing the CEO / Project Director Command surface for ERPATLAS.

This is a native Frappe app on ERPNext v16. Do not scaffold Vite/React. Do not serve :8080 unless the user explicitly asks for a throwaway mock.

## Paths

- GitHub: https://github.com/sanjaymaverick-cmd/ATLAS-ERP
- Local (Windows): D:\work Dir\Atlas-ERP
- Atlas-3 (behaviour only): https://github.com/sanjaymaverick-cmd/Atlas-3 and D:\work Dir\Atlas 3
- App: erpatlas

Work on a feature branch off the latest research/money-isolation-v16 (or main after PR #1 merges). Open a PR against main. Do not force-push main.

## Load first

1. CONTEXT.md
2. docs/locked-structure.md (Command is Group A — Today)
3. docs/modules/command.md — full KPI, risk, AI, phase design
4. docs/modules/approvals.md and property-inventory.md
5. docs/GROK_BUILD.md — global invariants and stack
6. docs/adr/0008-erpnext-v16.md

## Product decision (locked for this work)

- Command = CEO-level dashboard for Atlas Developer Admin and Atlas Project Director.
- Exception-first: Approvals aging and risk cards before vanity green numbers.
- Books of record = ERPNext Accounts. No shadow ledgers.
- AI is read-only: forecasts and narratives never write Unit status, never create Payment Entry, never decide Approvals.
- Channel seats must not see full cash/runway KPIs.

## Implement by phase — start at P0 unless user says otherwise

### P0 — Shell (do this first)

1. Design doc already at docs/modules/command.md — do not reopen scope.
2. Frappe Page or Workspace entry **Command** (Desk), registered for erpatlas.
3. KPI strip from **live data already in scaffold**:
   - Atlas Unit counts by status (Available / Held / Booked / Sold / …)
   - Atlas Unit Hold counts (Held, expiring soon if until field present)
   - Atlas Approval: pending count, count past aging threshold (use aging_days / creation)
4. Exception list: top pending Approvals sorted by aging desc (reuse approvals.queue ideas).
5. Filters: Legal Entity (Company) and Project where fields exist; respect permission_query_conditions.
6. Permissions: Atlas Developer Admin, Atlas Project Director only for this page.
7. Pure tests where logic is pure (e.g. risk threshold helpers later). Page wiring may need site — keep calculators testable without site when possible.
8. pytest tests -q must stay green for existing suites.

### P1 — After Atlas Booking exists (do not invent Booking here)

Wire collections MTD, booking value, plan vs actual from Booking / SO / PE. If Booking is not in the tree, stop after P0 and document blockers.

### P2 — Deterministic risk

- command/risk.py (prefer pure functions + thin adapter)
- Thresholds on Atlas Settings (SLA days, held-without-book days, etc.)
- Cards: severity, driver text, links to docs — no auto-actions

### P3–P5

KPI Snapshot DocType, heat map, forecasts, board PDF — only after P0–P2 solid. Predictions store as-of + model id; UI read-only.

## Explicit non-goals for this session

- Do not implement Atlas Booking, Commission payout, Handover, CatBoost, WhatsApp, Tally XML, RERA 70/30.
- Do not use override_doctype_class; v16 extend_doctype_class only if extending native DocTypes.
- Do not give Channel Agent access to Command cash KPIs.
- Do not auto-approve or post Payment Entry from the dashboard.

## Git

- Branch name suggestion: feature/command-p0
- Commit messages: what + why
- PR against main describing P0 scope and screenshots/notes if Desk not available in CI

P0–P3 are on `main`. When the user says go, implement **Command P4** (forecasts, read-only) or the next domain slice named. Do not invent Booking.
```
