# Research notes

Product source remains Atlas-3. These notes map Atlas-3 money and isolation rules onto ERPNext v16.

| # | Note | Status |
|---|---|---|
| 01 | [ERPNext v16](01-erpnext-v16.md) | Locked (ADR 0008) |
| 02 | [Booking ↔ Sales Order ↔ Payment Schedule + GST/advances](02-booking-sales-order-gst.md) | Scaffolded in Booking module |
| 03 | [Commission accounts + TDS](03-commission-tds.md) | Accrual JE + PI after Approved; TDS on Tax Withholding Category (CA) |
| 04 | [Concurrent unit lock on a bench](04-concurrent-lock.md) | CAS already in code; bench protocol open |
| 05 | [Channel isolation fixtures](05-channel-isolation-fixtures.md) | Query conditions + Role fixtures + daily report gate. User Permission is site data |
| 06 | [Payment Schedule GST logic](06-payment-schedule-gst.md) | Pure math + Booking collect adapter |


Rates and GST/TDS thresholds are **configuration for a CA**, not code constants. Confirm before go-live.
