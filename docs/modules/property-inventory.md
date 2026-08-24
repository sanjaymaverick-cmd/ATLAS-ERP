# Property Inventory — DocType design

**Atlas-3 sources:** `src/lib/sales/inventory.ts`, `src/lib/store.ts` (`holdUnit`, `releaseHold`, `bookHold`, `setUnitDispute`, `expireHolds`), `docs/sales/0001_inventory_channel.sql`, `docs/sales/PHASES.md` Phase 1, `scripts/trial/probes/unit-lock.mjs`.

**ERPNext:** Project (native). No native tower/unit lock.

## Acceptance (must remain true)

| Atlas-3 criterion | ERPATLAS rule |
|---|---|
| Unit cannot be held unless Available | `refuse_hold`; CAS `UPDATE … WHERE status='Available'` |
| Concurrent second hold refused | Unique live hold (`live_unit`) + CAS |
| Channel hold refused until today’s daily report | `refuse_hold_without_report` (Channel module injects the report fact) |
| Partner hold → booking waits in Approvals; unit stays Held | `bookHold` raises Approval kind `Hold booking`; does not move status |
| In-house bookHold books immediately | Agent without Channel Company / in-house flag |
| Release returns Available | Hold → Released, Unit Held → Available |
| Hold past `until` expires to Available | Daily job |
| Cancel booking returns Available (not if Possession) | Booking module; unit transition Booked → Available |
| Possession moves unit to Sold | Booking/Handover; also requires OC + closed snags + full collection |
| Pink City cannot see Desert Reach holds | Query conditions on Unit and Hold |
| Dispute is in-house overflow | Available / Held / Booked → Dispute only, not Channel |

ERPATLAS tightens Atlas-3 holes:

- A Possession booking still counts as live, so the unit cannot be booked again (`LIVE_BOOKING = Active | Possession`).
- Hold expiry only returns the unit to Available if it is still Held. Atlas-3 `expireHolds` always forced Available and could unlock a booked unit if the hold row was left live after convert/book.
- Hold `until` is inclusive (live through that calendar day). Expiry is a daily job, not lazy-on-next-hold.
- Booking must close the live hold row (Hold → Booked). Atlas-3 convert/addBooking could leave a Held row behind.

`Cancelled` is in the unit enum for Atlas-3 parity; no automatic path into it (booking cancel returns Available). Facing, parking, BHK, floor plans, and rate cards are sales talk in Atlas-3 — not fields in this slice.

## DocTypes

### Atlas Tower

| Field | Type | Req | Notes |
|---|---|---|---|
| naming_series | Data | | `ATW-.#####` |
| project | Link → Project | yes | |
| tower_name | Data | yes | |
| kind | Select | yes | Tower / Phase / Pocket |

### Atlas Unit

| Field | Type | Req | Notes |
|---|---|---|---|
| naming_series | Data | | `AUN-.#####` |
| project | Link → Project | yes | |
| tower | Link → Atlas Tower | yes | Must belong to same project |
| code | Data | yes | Unique with project (`project_code_key`) |
| kind | Select | yes | Flat / Shop / Plot |
| floor | Data | yes | Display grouping |
| area | Data | yes | Text, as in Atlas-3 |
| price | Currency | yes | |
| status | Select | yes | Available / Held / Booked / Sold / Cancelled / Dispute |
| project_code_key | Data | | Hidden, unique, `{project}::{code}` |
| events | Table → Atlas Unit Event | | Append-only |

Direct form edits of `status` are refused unless `frappe.flags.in_atlas_lock` or Dispute by an in-house seat.

### Atlas Unit Event (child)

| Field | Type | Notes |
|---|---|---|
| at | Datetime | |
| from_status | Select | Same options as Unit.status |
| to_status | Select | |
| note | Small Text | |
| actor | Link → User | |

### Atlas Unit Hold

| Field | Type | Req | Notes |
|---|---|---|---|
| naming_series | Data | | `AHD-.#####` |
| unit | Link → Atlas Unit | yes | |
| project | Link → Project | yes | Copied from unit |
| channel_company | Link → Atlas Channel Company | | Empty = in-house |
| agent | Link → User | yes | |
| customer_name | Data | yes | |
| until | Date | yes | |
| status | Select | yes | Held / Booked / Expired / Released |
| booking_requested | Check | | Set when a channel booking is queued |
| booking_value | Currency | | Stashed for the Approval |
| live_unit | Data | | Hidden unique: unit name while Held, else empty/NULL |

### Atlas Channel Company (minimal, isolation only)

Full Channel & Partner ships later. Inventory visibility needs this row now.

| Field | Type | Notes |
|---|---|---|
| company_name | Data | |
| city | Data | |
| gstin | Data | |
| status | Select | Invited / Active / Suspended |
| rate | Percent | Commission rate for later Booking |

User Permission on this DocType binds a Channel Agent / Admin to one firm.

## Status machine — Unit

```
Available ──hold──► Held ──book──► Booked ──possession──► Sold
    │                │               │
    │                release/expire  cancel (not if Possession)
    │                ▼               ▼
    └────────────► Available ◄───────┘
    │
    └── (Available|Held|Booked) ──dispute──► Dispute
```

`Cancelled` is in the enum for Atlas-3 parity; this slice has no automatic path into it.

Illegal: Held → Sold, Sold → anything, Dispute → anything (manual later), second Held.

## Status machine — Hold

```
Held ──release──► Released     (unit → Available)
Held ──expire──►  Expired      (unit → Available)
Held ──book──►    Booked       (unit → Booked; after Approval if channel)
```

Channel `book` while waiting: Hold stays **Held**, `booking_requested=1`, Approval kind `Hold booking` waiting on `Sales Manager / MD`.

## Server rules

1. `try_set_status(unit, from, to)` — `UPDATE tabAtlas Unit SET status=to WHERE name=? AND status=from`. Zero rows → refuse with the current status.
2. `before_insert` Hold: expire stale holds for that unit; channel daily-report gate (`atlas_has_today_report` hook from Channel; open until that module ships); `refuse_hold`; CAS Available → Held; set `live_unit`.
3. `bookHold(hold, value)`:
   - Hold must be Held.
   - If the agent has a Channel Company: raise Approval, do not book.
   - Else: Booking module `activate_from_hold` (CAS unit → Booked, close Hold, submit Sales Order, accrue Commission).
4. Channel query: Units where `status=Available` OR a Held hold exists for the user’s Channel Company. Holds: own company only.
5. In-house sees all units of Projects they may read.

## Whitelist

- `erpatlas.property_inventory.doctype.atlas_unit_hold.atlas_unit_hold.place_hold`
- `erpatlas.property_inventory.doctype.atlas_unit_hold.atlas_unit_hold.release_hold`
- `erpatlas.property_inventory.doctype.atlas_unit_hold.atlas_unit_hold.request_booking`
- `erpatlas.property_inventory.doctype.atlas_unit.atlas_unit.mark_dispute`

## Out of this slice

Daily report DocType, Handover, rate cards, parking, facing. Booking / Sales Order posting is the Booking module.
