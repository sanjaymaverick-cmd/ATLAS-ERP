# 04 — Concurrent unit lock on a bench

Atlas-3 acceptance: **Unit cannot be held unless Available; concurrent second hold is refused.**

## What the scaffold already does

[`erpatlas/property_inventory/lock.py`](../../erpatlas/property_inventory/lock.py) is pure (no frappe): transitions, refuse rules, live hold key.

[`erpatlas/property_inventory/lock_adapter.py`](../../erpatlas/property_inventory/lock_adapter.py) is the only writer of Unit.status:

```sql
SELECT status FROM `tabAtlas Unit` WHERE name = %s FOR UPDATE;
UPDATE `tabAtlas Unit` SET status = %s, modified = %s
  WHERE name = %s AND status = %s;
```

`live_unit` unique key on Atlas Unit Hold: while status is Held, `live_unit` = unit name → second live hold cannot insert.

This is **pessimistic CAS** (row lock) plus a unique index. It matches the Atlas-3 SQL contract `UPDATE … WHERE status = 'available' RETURNING`.

`frappe.db.set_value` is **not** sufficient: it does not `FOR UPDATE` and does not fail closed on a stale status.

## What a real bench must prove

Pure tests (`tests/test_unit_lock.py`) do not talk to MariaDB. Before Booking work, run this on a v16 site:

1. Seed one Available unit.
2. Open two bench console / two HTTP requests in the same second, both `hold` that unit.
3. Expect: exactly one Hold row status Held, unit status Held; the other throws the refuse string.
4. Repeat Available → Book (in-house) vs Hold, mixed.
5. Expire job must **not** set Available if the unit is already Booked (adapter already guards this).

Suggested driver (site required):

```python
# two threads, shared site
frappe.connect(site)
# thread A and B: frappe.db.begin(); cas_status(...); frappe.db.commit()
```

Use **autocommit off**. `FOR UPDATE` only holds until COMMIT. If hold insert and CAS are in different transactions, a gap exists: insert Hold then CAS can interleave. **Rule:** one `frappe.db.begin()` around unique Hold insert + `cas_status`. Rollback both on CAS false.

## Engine notes (v16)

| Engine | `FOR UPDATE` | Unique `live_unit` |
|---|---|---|
| MariaDB InnoDB (default) | Yes | Yes |
| Postgres | Yes | Yes |

Keep raw SQL in `lock_adapter` only. Quote table `tabAtlas Unit`.

After CAS, `get_doc` + append events + `save` runs with `frappe.flags.in_atlas_lock`. If save fails, the status may already have moved — catch and reverse or re-read. Track this as a test case.

## Not in this slice

Redis locks, advisory locks, or application-level mutexes. Row lock + unique key is the contract.
