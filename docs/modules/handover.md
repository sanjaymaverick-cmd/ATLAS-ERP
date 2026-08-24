# Handover & Possession

**Atlas-3 sources:** `HandoverCase`, `Snag`, `markPossession`, `advanceHandover`, `setHandoverOc`, `closeSnag`.

**Invariant:** Possession is blocked until Occupancy Certificate is received **and** snags are closed **and** the payment plan is fully collected. Then the Unit moves Booked → Sold. Booking status becomes Possession.

Atlas-3 split this: `markPossession` only checked collection; `advanceHandover` checked OC + snags and did not sell the unit. ERPATLAS **one gate** `grant_possession`.

## DocTypes

### Atlas Handover Case

| Field | Type | Notes |
|---|---|---|
| naming_series | | `AHO-.#####` |
| booking | Link → Atlas Booking | Unique live case per booking |
| unit | Link → Atlas Unit | |
| project | Link → Project | |
| channel_company | Link → Atlas Channel Company | Copied from booking (isolation) |
| occupancy_certificate | Select | Pending / Received |
| snags_open | Int | Count of Open snags on the unit |
| status | Select | Snagging / Possession / Society / Defect |

Created when a Booking becomes Active (`ensure_handover`). Direct status edits refused.

### Atlas Snag

| Field | Type | Notes |
|---|---|---|
| naming_series | | `ASG-.#####` |
| unit | Link → Atlas Unit | |
| project | Link → Project | |
| handover | Link → Atlas Handover Case | |
| title | Data | |
| status | Select | Open / Closed |

## Server rules

1. `refuse_possession` — Occupancy Certificate Received, `open_snags == 0`, `plan_collected >= plan_gross`, booking Active, unit Booked.
2. `grant_possession` — that gate, then CAS unit Booked → Sold, booking → Possession, case → Possession.
3. Channel seats may read their case; they cannot receive Occupancy Certificate or grant possession.
4. Society / Defect stages are stored for Atlas-3 parity; this slice only implements Snagging → Possession.

## Whitelist

- `erpatlas.handover.doctype.atlas_handover_case.atlas_handover_case.receive_occupancy_certificate`
- `erpatlas.handover.doctype.atlas_handover_case.atlas_handover_case.grant_possession`
- `erpatlas.handover.doctype.atlas_snag.atlas_snag.close_snag`
