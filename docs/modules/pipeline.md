# Lead & Pipeline

**Atlas-3 sources:** `ingestLead`, `findDuplicate`, `normalizePhone`, `PIPELINE` stages, `scoring.ts` CatBoost payload.

**ERPNext:** native **Lead**. Custom Atlas fields. `extend_doctype_class` mixin — not `override_doctype_class`.

## Acceptance

| Atlas-3 | ERPATLAS |
|---|---|
| Dedup same phone on the same Project (not lost/nurture) | `find_duplicate` + unique `atlas_live_phone` |
| Ingest starts at inquiry | `atlas_stage=inquiry` |
| CatBoost is external `cat_features` | `pipeline.score.catboost_payload`; HTTP `frappe.conf.atlas_scoring_url` |
| Host never re-implements Ordered Target Statistics | Hybrid fallback is additive points only |
| Channel isolation | `Lead.atlas_channel_company` query conditions |

Won does **not** create an Atlas Booking in this slice. Booking stays ADR 0007.

## Fields on Lead

`atlas_project`, `atlas_unit`, `atlas_channel_company`, `atlas_stage`, `atlas_source`, `atlas_kind`, `atlas_budget`, `atlas_score`, `atlas_band`, `atlas_score_model`, `atlas_live_phone`.

## Whitelist

- `erpatlas.pipeline.intake.ingest_lead`
- `erpatlas.pipeline.intake.advance_lead`
