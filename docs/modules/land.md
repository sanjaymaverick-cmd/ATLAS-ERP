# Land & Legal — parcels, diligence, statutory filings

**Seats:** Atlas Land Legal, Atlas Developer Admin. Project Director reads.

**Atlas-3:** identified → diligence → acquired. Acquire is disabled until every diligence item is **clear**. Obligations (RERA / labour / insurance / tax) stay filing dates — not a 70/30 bank split.

## Atlas Parcel

Status: `identified` → `diligence` → `acquired` (`closed` is terminal). Status is locked on the form; use **Start standard title pack** or **Acquire**.

| Field | Rule |
|---|---|
| Title + khasra | Required to create |
| RERA target | Planned number only — not a filed obligation |
| Consideration + sale deed number | Required to acquire |

Acquire does **not** create a Payment Entry and does **not** post to Tally.

## Atlas Diligence Item

Per parcel. Status: `open` / `clear` / `flagged`. Adding the first item (or the standard pack) moves an identified parcel to diligence.

**Standard title pack** (Jaipur residential, Atlas-3):

1. Title search — 30 year
2. Encumbrance certificate
3. Conversion / CLU
4. Mutation in revenue record
5. Access road NOC

Refuse acquire while any item is open or flagged; the reason lists those titles. Empty pack: "Open the title pack before acquisition."

## Atlas Obligation

Unchanged: due dates, overdue, filed with challan ref. Not RERA 70/30 escrow.

## Atlas Instalment

Ops reminder on a Parcel (due / paid). **Record paid** does not create a Payment Entry and does not post to Tally. ERPNext remains the books.

## Out of scope here

- RERA 70/30 bank split
- Land consideration as a Journal Entry / Payment Entry
