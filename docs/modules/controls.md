# Controls — materials and quantity variance

**Seats:** Atlas Stores, Atlas Site, Atlas Developer Admin. Project Director reads (and may lock quantity).

**Primary question:** Can we issue this quantity without breaking the receipt ledger? Does site measure match the drawing?

## Atlas Material

Received / issued on one row. Issue refuses if qty would exceed accepted receipts. This desk counts quantity — it is not ERPNext Stock Entry and not a Payment Entry.

## Atlas Quantity

Drawing qty vs site measure.

| Status | When |
|---|---|
| provisional | Drawing qty equals site measure |
| variance | Numbers do not match (chip) |
| approved | Locked after **Approve quantity** |

Variance = site measure − drawing qty. Approved rows cannot change qty or status. Approve does **not** create a Payment Entry and does **not** write a Unit.

On-screen: “Drawing qty”, not BIM. Cost code is WBS.

## Out of scope here

- Valued stock / GRN in ERPNext
- BIM / DWG viewer
- Auto-pay or auto-issue from a variance chip
