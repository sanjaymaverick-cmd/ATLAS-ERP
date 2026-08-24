# Module designs

Implementable DocType designs. High-level map is locked in `docs/locked-structure.md`.

| Module | Design | Status |
|---|---|---|
| Property Inventory | [property-inventory.md](property-inventory.md) | Scaffolded |
| Approvals | [approvals.md](approvals.md) | Scaffolded |
| Command (CEO) | [command.md](command.md) | P0–P5 (board-pack PDF from Command JSON) |
| Capital | Atlas Funding Sanction, Budget Line | Loan % + equity % = 100; budget vs committed |
| Audit | Atlas Audit Event | Append-only trail |
| Sales Analytics | [analytics.md](analytics.md) | Funnel counts + model monitor (CatBoost external) |
| Books | [books.md](books.md) | Recon / exception cases. Atlas never posts |
| Channel & Partner | [channel.md](channel.md) | Daily report + agent roster (UP at runtime, not fixtures) + exclusive project lock |
| Lead & Pipeline | [pipeline.md](pipeline.md) | Native Lead ingest/dedup; CatBoost external |
| Booking | [booking.md](booking.md) | Scaffolded — Active → SO, collect, commission Accrued |
| Handover | [handover.md](handover.md) | Occupancy Certificate + snags + full collection → Sold |
| Commission (books) | [research/03](../research/03-commission-tds.md) | Accrual JE (if accounts set); PI after Approved; TDS via ERPNext Tax Withholding. No PE from Approvals |
| Commercial | Vendor Active + GSTIN before PO | Scaffolded |
| Quotations | [quotations.md](quotations.md) | Lowest Active-vendor quote may become a PO |
| Documents | [documents.md](documents.md) | Four-eyes + single-use Export Grant. Drawing register (no viewer) |
| Site | [site.md](site.md) | Diary one-seal-per-device-day; inspection fail raises NCR |
| Change Control | [change-control.md](change-control.md) | RFI response closes; NCR needs Pass re-inspection; VO → Approval |
| Controls | [controls.md](controls.md) | Receive/issue; drawing vs site measure; approve locks variance |
| Land & Legal | [land.md](land.md) | Parcel + title pack; acquire only when diligence is clear. Instalment is ops-only. Not 70/30 |
| Organization | Owner Decision, Assistant Note | Assistant draft-only |
| Communications | Atlas Wa Template | Registry only — no send |

Platform: ERPNext **v16** — [ADR 0008](../adr/0008-erpnext-v16.md), [research/01](../research/01-erpnext-v16.md).

Grok Build prompts: [GROK_BUILD.md](../GROK_BUILD.md) (base), [GROK_BUILD_COMMAND.md](../GROK_BUILD_COMMAND.md) (CEO Command).

When a new module is designed, add a file here and map every rule to Atlas-3 acceptance.
