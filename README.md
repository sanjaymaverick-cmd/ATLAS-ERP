# ERPATLAS

Real-estate ERP as a **native custom Frappe app** on ERPNext **v16**. One system — no separate frontend. Atlas-3 is the product source; ERPNext Accounts is the books of record.

## Status

Locked: module map, roles, invariants (`docs/locked-structure.md`). Target stack: Frappe + ERPNext `version-16` (Python 3.14). See `docs/adr/0008-erpnext-v16.md`.

This cut: **Property Inventory** (Unit lock, Hold, Tower) and **Approvals** (unified queue). Channel Company exists only so inventory isolation has a row to bind.

Research (Booking ↔ SO, GST, commission/TDS, CAS, isolation fixtures): `docs/research/`.

## Install (bench)

```bat
cd %BENCH%
bench get-app erpatlas "D:\work Dir\Atlas-ERP"
bench --site SITE install-app erpatlas
```

Requires `erpnext` on version-16.

## Tests that do not need a site

```bat
cd "D:\work Dir\Atlas-ERP"
python -m pytest tests -q
```

## Language

`CONTEXT.md`. Three different “companies”: Legal Entity (ERPNext Company), Channel Company (agency), and the books company — see `docs/adr/0005-three-company-words.md`.
