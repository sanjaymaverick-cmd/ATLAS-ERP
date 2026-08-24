# ERPATLAS

Real-estate ERP as a **native custom Frappe app** on ERPNext. One system — no separate frontend. Atlas-3 is the product source; ERPNext Accounts is the books of record.

## Status

Locked: module map, roles, invariants (`docs/locked-structure.md`).

This cut: **Property Inventory** (Unit lock, Hold, Tower) and **Approvals** (unified queue). Channel Company exists only so inventory isolation has a row to bind.

## Install (bench)

```bat
cd %BENCH%
bench get-app erpatlas "D:\work Dir\Atlas-ERP"
bench --site SITE install-app erpatlas
```

Requires `erpnext`.

## Tests that do not need a site

```bat
cd "D:\work Dir\Atlas-ERP"
python -m pytest tests -q
```

## Language

`CONTEXT.md`. Three different “companies”: Legal Entity (ERPNext Company), Channel Company (agency), and the books company — see `docs/adr/0005-three-company-words.md`.
