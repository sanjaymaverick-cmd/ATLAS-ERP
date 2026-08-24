# 05 — Channel isolation fixtures

**Invariant:** Pink City never sees Desert Reach holds, reports, or leads. Isolation is **server query conditions**, not hidden UI.

Query conditions already live in [`erpatlas/property_inventory/permissions.py`](../../erpatlas/property_inventory/permissions.py):

- Channel seats: Units that are **Available** (inventory to sell) **or** Held by **their** Channel Company.
- Holds: `channel_company =` the user’s User Permission.
- Channel Company list: only their row.

Binding today: `frappe.defaults.get_user_permissions(user)["Atlas Channel Company"]`.

Fixtures must make that binding real on a fresh site.

## What to ship in the app (versioned)

### 1. Roles (fixtures)

Export Role records (not System Manager):

- Atlas Developer Admin
- Atlas Project Director
- Atlas Sales Manager
- Atlas Channel Admin
- Atlas Channel Agent
- Atlas Commercial
- Atlas Finance
- Atlas Site
- Atlas Stores
- Atlas Land Legal
- Atlas Documents

`hooks.py`:

```python
fixtures = [
    {"dt": "Role", "filters": [["name", "in", ATLAS_ROLES]]},
    {"dt": "Custom DocPerm", "filters": [["role", "in", ATLAS_ROLES]]},
]
```

Role permissions belong **on the DocType JSON** (`permissions` array) plus Custom DocPerm only if we must grant native ERPNext DocTypes (Customer, Project, Sales Order) to Atlas roles.

### 2. DocType permissions (already on JSON)

Channel Agent / Admin:

| DocType | Channel Agent | Channel Admin |
|---|---|---|
| Atlas Unit | read | read |
| Atlas Unit Hold | read, write, create | read, write, create |
| Atlas Channel Company | read (own) | read, write (own roster later) |
| Atlas Approval | read (own refs) | read |
| Atlas Booking (later) | read own | read own company |

They never get `submit` on Atlas Approval.

`apply_user_permissions` must be **1** on these DocTypes for Channel roles (Desk checkbox “Apply User Permissions”). Without it, query conditions still apply via `permission_query_conditions` hook — keep **both**: hook for list/report SQL, User Permission for the standard engine.

### 3. User Permission is per user — do not fixture production users

User Permission rows (`user` + `allow=Atlas Channel Company` + `for_value=Pink City`) are **site data**.

`after_install` (demo only, gated):

```python
# if frappe.conf.get("atlas_seed_demo"):
#   create Channel Company Pink City / Desert Reach
#   create users ag@ / ca@ with Role Atlas Channel Agent / Admin
#   frappe.get_doc({"doctype": "User Permission",
#       "user": "ag@atlas.local",
#       "allow": "Atlas Channel Company",
#       "for_value": pink_city_name,
#       "apply_to_all_doctypes": 1}).insert()
```

Production: Company Admin UI “Invite agent” creates the User + User Permission. Never a global fixture of emails.

### 4. In-house seats

Sales Manager / Developer Admin: **no** User Permission on Channel Company. `permissions.py` already returns `""` (unrestricted) for Developer Admin and non-channel roles. Confirm Sales Manager is **not** in `CHANNEL_ROLES`.

### 5. Legal Entity vs Channel Company

Do **not** isolate Channel seats with ERPNext `Company` User Permissions. Channel agencies are not Legal Entities (ADR 0005). Project.company (Legal Entity) still filters books; Channel query uses `Atlas Channel Company` only.

If a site also uses Company User Permissions for multi-developer groups, stack them: `AND` in SQL. Write an explicit test: SM of Legal Entity A must not see units of Legal Entity B; Channel of Pink City must not see Desert Reach even inside A.

## Tests without a site

Keep pure tests for the SQL fragment builder (pass a fake `channel_company_for`). Add a site test later: two users, `frappe.get_list("Atlas Unit Hold")` lengths.

## Gaps vs Atlas-3

- Daily report gate is still injected by Channel module (not shipped).
- Leads / pipeline isolation is not in this slice (same User Permission will apply once Lead has `channel_company`).
- `has_unit_permission` currently hides Booked/Sold units from Channel. Confirm product: agents usually need to see *their* booked units. **Proposed change:** Channel may read a Unit if they have a Hold or Booking on it, not only Held. Record before Booking module ships.
