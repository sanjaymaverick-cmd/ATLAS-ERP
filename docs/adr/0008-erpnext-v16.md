# Target ERPNext / Frappe version-16

Product decision (2026-08-24): ERPATLAS develops and deploys on **Frappe version-16 + ERPNext version-16**.

Consequences:

- Use `extend_doctype_class` (mixin, stackable) instead of `override_doctype_class` when extending Sales Order, Payment Entry, Supplier, Project.
- Official `frappe` `version-16` `pyproject.toml` requires **Python `>=3.14,<3.15`**. The bench must match. Do not assume 3.10/3.12.
- `add_to_apps_screen` in `hooks.py` is required for Desk in v16.
- `required_apps = ["erpnext"]` stays.

Do not target v15. If a host is stuck on v15, that is a separate fork, not this app.
