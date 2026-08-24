# 01 — ERPNext / Frappe version-16

**Decision:** locked in [ADR 0008](../adr/0008-erpnext-v16.md).

## Why v16

- `extend_doctype_class` lets ERPATLAS mixin methods onto Sales Order, Payment Entry, Supplier, Project without winning an override war against other apps.
- ERPNext v16 is the current major line (production-ready from late 2025).
- Desk apps screen, list UX, and financial report templates are v16-native.

## Hard constraints for the bench

| Layer | Pin |
|---|---|
| Frappe | `version-16` branch |
| ERPNext | `version-16` branch |
| Python | **`>=3.14,<3.15`** (official `frappe/pyproject.toml` on version-16) |
| Database | MariaDB 10.8+ (default). Postgres is supported by Frappe; CAS SQL in `lock_adapter` uses `FOR UPDATE` which both accept |
| App | `erpatlas` with `required_apps = ["erpnext"]` |

Windows: run the bench in **WSL2 Ubuntu**, not native Windows. Clone `D:\work Dir\Atlas-ERP` into the WSL filesystem or a `/mnt` path only if I/O is acceptable.

## Hooks we will use (v16)

```python
extend_doctype_class = {
    "Sales Order": ["erpatlas.books.sales_order.SalesOrderMixin"],
    "Payment Entry": ["erpatlas.books.payment_entry.PaymentEntryMixin"],
    "Supplier": ["erpatlas.commercial.supplier.SupplierMixin"],
}

add_to_apps_screen = [{
    "name": "erpatlas",
    "logo": "/assets/erpatlas/logo.png",
    "title": "ERPATLAS",
    "route": "/app/erpatlas",
}]
```

Prefer `doc_events` for validate/on_submit. Prefer `extend_doctype_class` when we need extra methods. Avoid `override_doctype_class`.

## What this does *not* change

- Custom DocTypes (`Atlas Unit`, `Atlas Approval`, later `Atlas Booking`) stay in this app.
- Native objects remain Company, Project, Customer, Sales Order, Sales Invoice, Payment Entry, Journal Entry, Supplier, Purchase Invoice.

## Open (ops, not product)

- Exact patch of version-16 on the first bench (`bench version`).
- Frappe Cloud vs self-host. Both must be v16.
