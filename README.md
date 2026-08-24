# ERPATLAS

Real-estate ERP as a **native custom Frappe app** on ERPNext **v16**. One system — no separate frontend. Atlas-3 is the product source; ERPNext Accounts is the books of record.

## Status (main @ 2026-08-24)

Locked: module map, roles, invariants (`docs/locked-structure.md`). Stack: Frappe + ERPNext `version-16` (Python 3.14) — `docs/adr/0008-erpnext-v16.md`.

**Modules on main** (`erpatlas/modules.txt`)

| Module | What’s in the tree |
|---|---|
| Property Inventory | Unit / Tower / Hold / Channel Company; CAS lock |
| Approvals | Unified `Atlas Approval` queue |
| Booking | Booking + payment steps + Commission Accrued; Active → SO; collect |
| Handover | Handover Case + Snag; possession gates |
| Channel | Daily Report + hold gate |
| Pipeline | Lead ingest / score hooks |
| Documents | Controlled Document + Export Grant (four-eyes) |
| Command | CEO Desk page; KPIs + risk helpers |
| Books | `payment_gst`, commission adapter, SO mixin |

**Research:** `docs/research/01`–`06`.

**Still open / harden next**

1. Bench install + site tests (CAS race, Booking→SO on real ERPNext)
2. Commission JE / TDS PI end-to-end on a site
3. Command money KPIs + risk thresholds tuned on Atlas Settings
4. CatBoost external bind, WhatsApp, Tally XML, RERA — only when named

## Install (bench)

```bat
cd %BENCH%
bench get-app erpatlas "D:\work Dir\Atlas-ERP"
bench --site SITE install-app erpatlas
```

Requires `erpnext` on version-16. Windows: WSL2.

## Sync this folder

```bat
cd "D:\work Dir\Atlas-ERP"
git fetch origin
git checkout main
git pull origin main
python -m pytest tests -q
```

## Grok Build / CLI

- Base: `docs/GROK_BUILD.md`
- CEO Command: `docs/GROK_BUILD_COMMAND.md`

## Language

`CONTEXT.md`. Legal Entity = ERPNext Company; Channel Company = agency (not a Company). Unit is the lock. Booking ≠ Sales Order ≠ Payment Entry.
