# Module designs

Implementable DocType designs. High-level map is locked in `docs/locked-structure.md`.

| Module | Design | Status |
|---|---|---|
| Property Inventory | [property-inventory.md](property-inventory.md) | Scaffolded |
| Approvals | [approvals.md](approvals.md) | Scaffolded |
| Command (CEO) | [command.md](command.md) | Design locked; P0 next |
| Channel & Partner | — | Channel Company row only (isolation). Fixtures: [research/05](../research/05-channel-isolation-fixtures.md) |
| Booking | — | **Next domain slice.** Contract: [research/02](../research/02-booking-sales-order-gst.md) |
| Commission (books) | — | Contract: [research/03](../research/03-commission-tds.md) |
| Documents / Commercial / Site / … | — | not started |

Platform: ERPNext **v16** — [ADR 0008](../adr/0008-erpnext-v16.md), [research/01](../research/01-erpnext-v16.md).

Grok Build prompts: [GROK_BUILD.md](../GROK_BUILD.md) (base), [GROK_BUILD_COMMAND.md](../GROK_BUILD_COMMAND.md) (CEO Command).

When a new module is designed, add a file here and map every rule to Atlas-3 acceptance.
