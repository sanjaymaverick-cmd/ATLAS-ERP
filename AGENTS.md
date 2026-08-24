# ERPATLAS

Native Frappe app on ERPNext. Atlas-3 (`D:\work Dir\Atlas 3`) is the product source for behaviour. This repo is the runtime.

## Always load

- `docs/locked-structure.md` — modules, roles, invariants. Do not re-open unless the user explicitly changes them.
- `CONTEXT.md` — words. Challenge a conflicting term immediately.

## When designing or changing a DocType

1. Prefer an ERPNext object. Custom only when Atlas-3 has logic ERPNext does not provide.
2. Map every field, status, and server rule back to Atlas-3 acceptance (`docs/sales/PHASES.md` in Atlas-3, copied into `docs/modules/*` here).
3. Company isolation, unit lock, commission accrual, and four-eyes are first-class.
4. Write the rule in a deep module (`property_inventory.lock`, `approvals.queue`) and keep the controller thin.

## Invariants (never break)

- Unit cannot be held unless Available; concurrent second hold is refused.
- Commission accrues only — never auto-pays and never creates a Payment Entry from Approvals.
- Possession is blocked until snags are closed and OC is received.
- No PO until the vendor is Active (GSTIN required).
- Document export is four-eyes + single-use grant.
- Atlas never posts to Tally.
- Channel companies never see each other’s data (server query conditions, not UI hide).

## Layout

- `erpatlas/` — Frappe app package
- `docs/adr/` — hard-to-reverse choices
- `docs/modules/` — implementable DocType designs
- `tests/` — pure tests (no site required)

Pure tests: `python -m pytest tests -q` from the repo root.
