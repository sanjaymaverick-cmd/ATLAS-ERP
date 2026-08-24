# Module designs

Implementable DocType designs. High-level map is locked in `docs/locked-structure.md`.

| Module | Design | Status |
|---|---|---|
| Property Inventory | [property-inventory.md](property-inventory.md) | Scaffolded |
| Approvals | [approvals.md](approvals.md) | Scaffolded |
| Channel & Partner | — | Channel Company row only (isolation). Fixtures: [research/05](../research/05-channel-isolation-fixtures.md) |
| Booking | [booking.md](booking.md) | Scaffolded — Active → SO, collect, commission Accrued |
| Commission (books) | — | Accrual row on Booking. JE / TDS PI still [research/03](../research/03-commission-tds.md) |
| Documents / Commercial / Site / … | — | not started |

Platform: ERPNext **v16** — [ADR 0008](../adr/0008-erpnext-v16.md), [research/01](../research/01-erpnext-v16.md).

When a new module is designed, add a file here and map every rule to Atlas-3 acceptance.
