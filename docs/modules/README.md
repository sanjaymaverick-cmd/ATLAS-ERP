# Module designs

Implementable DocType designs. High-level map is locked in `docs/locked-structure.md`.

| Module | Design | Status |
|---|---|---|
| Property Inventory | [property-inventory.md](property-inventory.md) | Scaffolded |
| Approvals | [approvals.md](approvals.md) | Scaffolded |
| Command (CEO) | [command.md](command.md) | P0–P2 (counts, Booking money, deterministic risk). P3 snapshot next |
| Channel & Partner | [channel.md](channel.md) | Daily report gate + Role fixtures. User Permission still site data |
| Booking | [booking.md](booking.md) | Scaffolded — Active → SO, collect, commission Accrued |
| Handover | [handover.md](handover.md) | Occupancy Certificate + snags + full collection → Sold |
| Commission (books) | [research/03](../research/03-commission-tds.md) | Accrual JE (if accounts set); PI after Approved; TDS via ERPNext Tax Withholding. No PE from Approvals |
| Commercial | Vendor Active + GSTIN before PO | Scaffolded. RFQ/PO flow not started |
| Documents / Site / … | — | not started |

Platform: ERPNext **v16** — [ADR 0008](../adr/0008-erpnext-v16.md), [research/01](../research/01-erpnext-v16.md).

Grok Build prompts: [GROK_BUILD.md](../GROK_BUILD.md) (base), [GROK_BUILD_COMMAND.md](../GROK_BUILD_COMMAND.md) (CEO Command).

When a new module is designed, add a file here and map every rule to Atlas-3 acceptance.
