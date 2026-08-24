# Booking is operational; Sales Order is the books document

Atlas Booking (later module) owns the unit lock, partner, payment steps, handover case, and commission accrual. When a Booking becomes Active, ERPATLAS creates an ERPNext Sales Order for the same Customer / amount so Accounts stays the books of record. A Hold never creates a Sales Order. Approving commission never creates a Payment Entry.

**Considered options:** use Sales Order as the booking (rejected — possession, snags, and commission accrual are not Sales Order behaviour); keep bookings off the books (rejected — contradicts ERPNext-as-books).
