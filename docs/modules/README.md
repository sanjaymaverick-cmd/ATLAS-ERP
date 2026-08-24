# Module designs

Implementable DocType designs. High-level map is locked in `docs/locked-structure.md`.

| Module | Design | Status |
|---|---|---|
| Property Inventory | [property-inventory.md](property-inventory.md) | Scaffolded |
| Approvals | [approvals.md](approvals.md) | Scaffolded |
| Command (CEO) | [command.md](command.md) | P0–P5 (board-pack PDF from Command JSON) |
| Capital | Atlas Funding Sanction | Loan % + equity % = 100 |
| Audit | Atlas Audit Event | Append-only trail |
| Channel & Partner | [channel.md](channel.md) | Daily report gate + Role fixtures. User Permission still site data |
| Lead & Pipeline | [pipeline.md](pipeline.md) | Native Lead ingest/dedup; CatBoost external |
| Booking | [booking.md](booking.md) | Scaffolded — Active → SO, collect, commission Accrued |
| Handover | [handover.md](handover.md) | Occupancy Certificate + snags + full collection → Sold |
| Commission (books) | [research/03](../research/03-commission-tds.md) | Accrual JE (if accounts set); PI after Approved; TDS via ERPNext Tax Withholding. No PE from Approvals |
| Commercial | Vendor Active + GSTIN before PO | Scaffolded |
| Quotations | [quotations.md](quotations.md) | Lowest Active-vendor quote may become a PO |
| Documents | [documents.md](documents.md) | Four-eyes + single-use Export Grant |
| Site | [site.md](site.md) | Diary one-seal-per-device-day; inspection fail raises NCR |
| Change Control | Atlas Change Item | NCR from inspection; close NCR; VO amount → Approval kind Change |
| Controls | Atlas Material | Cannot issue more than received |
| Land & Legal | Atlas Obligation | RERA/labour/insurance/tax filings. Not 70/30 bank split |
| Organization | Owner Decision, Assistant Note | Assistant draft-only |
| Communications | Atlas Wa Template | Registry only — no send |

Platform: ERPNext **v16** — [ADR 0008](../adr/0008-erpnext-v16.md), [research/01](../research/01-erpnext-v16.md).

Grok Build prompts: [GROK_BUILD.md](../GROK_BUILD.md) (base), [GROK_BUILD_COMMAND.md](../GROK_BUILD_COMMAND.md) (CEO Command).

When a new module is designed, add a file here and map every rule to Atlas-3 acceptance.
