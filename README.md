# ERPATLAS

Real-estate ERP as a **native custom Frappe app** on ERPNext **v16**. One system — no separate frontend. Atlas-3 is the product source; ERPNext Accounts is the books of record.

## Status (main @ 2026-08-24)

Locked: module map, roles, invariants (`docs/locked-structure.md`). Stack: Frappe + ERPNext `version-16` (Python 3.14) — `docs/adr/0008-erpnext-v16.md`.

**Scaffolded on main**

| Area | What’s in the tree |
|---|---|
| Property Inventory | Atlas Unit / Tower / Hold / Channel Company; CAS lock |
| Approvals | Unified `Atlas Approval` queue |
| Booking | Atlas Booking + payment steps + Commission Accrued; Active → SO; collect (GST math) |
| Books helpers | `payment_gst.py`, SO mixin, posting stubs |
| Command (CEO) | Desk page + Workspace; P0 KPIs (units, holds, approvals aging) |
| Research | `docs/research/01`–`06` (v16, Booking↔SO, commission/TDS, CAS, isolation, GST) |

**Next (pick one branch at a time)**

1. Handover & Possession (OC + snags + full collection → Unit Sold)
2. Commission JE / TDS Purchase Invoice (research/03) — still no PE from Approvals
3. Channel role fixtures + daily-report gate (research/05)
4. Command P1 money KPIs (booking value, collections from PE)
5. Command P2 deterministic risk cards

Not next unless named: CatBoost, WhatsApp, Tally XML, RERA 70/30, full AI forecasts.

## Install (bench)

```bat
cd %BENCH%
bench get-app erpatlas "D:\work Dir\Atlas-ERP"
bench --site SITE install-app erpatlas
```

Requires `erpnext` on version-16. Windows: WSL2.

## Tests (no site required)

```bat
cd "D:\work Dir\Atlas-ERP"
python -m pytest tests -q
```

## Grok Build / CLI

- Base brief: `docs/GROK_BUILD.md`
- CEO Command: `docs/GROK_BUILD_COMMAND.md`

## Language

`CONTEXT.md`. Legal Entity = ERPNext Company; Channel Company = agency (not a Company). Unit is the lock. Booking ≠ Sales Order ≠ Payment Entry.
