# ERPATLAS

A real-estate ERP that lives entirely inside ERPNext + Frappe. ERPNext Accounts is the books of record. Atlas-3 is the product source for behaviour and acceptance, not the runtime.

## Language

### Organisations

**Legal Entity**:
A GST-registered developer company that owns projects. In this system it is ERPNext Company.
_Avoid_: firm (for developers), channel company, partner

**Channel Company**:
An external agency that sells units for a fee. Isolated from every other agency. Not an ERPNext Company.
_Avoid_: partner firm as a Legal Entity, Company (unqualified)

**Project**:
A named development owned by one Legal Entity. ERPNext Project, with Atlas fields.
_Avoid_: site (the physical place of work), phase (a tower grouping)

### Inventory

**Tower**:
A named grouping of units inside a Project: a tower, a phase, or a pocket.

**Unit**:
A sellable flat, shop, or plot. Status is the lock. The unit is the source of truth for whether anyone may hold or book it.
_Avoid_: Item, warehouse bin, property (unqualified)

**Hold**:
A time-bounded lock of one Available Unit for one named buyer. A second live Hold on the same Unit is refused.
_Avoid_: reservation, lock (unqualified), blocked

**Booking**:
A confirmed sale of one Unit to one Customer. Commission may accrue here. It is not a Payment Entry.
_Avoid_: Sales Order (the later books document), allotment (a booking paper)

### Land

**Parcel**:
A plot of land for a Project. Status is identified → diligence → acquired.
_Avoid_: site (the physical place of work), Unit (a sellable flat)

**Khasra**:
The revenue survey number of a Parcel.

**Diligence**:
Title, conversion, road and other checks before you buy the land. Each item is open, clear, or flagged. Acquisition waits until every item is clear.
_Avoid_: due diligence as a free-text note on the Project

### Approvals

**Approval**:
One row in the unified decision queue. Money is not spent and originals are not released until a named waiter says yes or no.
_Avoid_: Workflow (ERPNext per-DocType workflow), request (unqualified)

**Waiting On**:
The named seat that must act on an Approval. Routing is a closed list, not free text.

**Four-eyes**:
Two distinct people must be involved before an original document is released. The export grant is single-use.

**Export Grant**:
Permission to download one original once. Pending → Granted → Used (or Rejected / Expired).

### Money and books

**Books of Record**:
ERPNext Accounts. Journals and Payment Entries live here.
_Avoid_: Tally (except as a one-time XML import), Atlas books

**Commission**:
A partner earning counted at Booking. Status starts Accrued. Approval may mark it Approved. Nothing here creates a Payment Entry.
_Avoid_: payout, payment (for the accrual itself)

**Tally**:
A legacy desktop ledger used only to import opening XML. Atlas never posts to Tally.

### Handover

**Occupancy Certificate**:
Authority permission to live in the building. Keys wait for it.
_Avoid_: OC as the only on-screen label (chip is plain English; short form is hover)

**Snag**:
A defect on a Unit that must be closed before keys.

**Possession**:
Keys given. Blocked while Snags are open, Occupancy Certificate is missing, or the payment plan is not fully collected. Moves the Unit to Sold.

### Controls

**Drawing quantity**:
How much material the drawings say you need.
_Avoid_: BIM as the only on-screen label

**Site measure**:
What was measured on site.

**Quantity variance**:
Drawing quantity versus site measure. Status is provisional, variance, or approved. Approve locks the numbers; it is not a Payment Entry.

**Instalment**:
A land-loan reminder on a Parcel. Marking it paid is ops only. ERPNext remains the books.
_Avoid_: Payment Entry (for this reminder), Tally voucher

**Books case**:
A recon or exception against company accounts. Atlas never posts a voucher from it.

### Seats

**Atlas Developer Admin**:
Full-access managing director seat (`md@`).
_Avoid_: owner (code from Atlas-3), System Manager (Frappe, keep distinct)

**Atlas Channel Agent** / **Atlas Channel Admin**:
Seats that see only their Channel Company.
_Avoid_: channel (unqualified), third-party (in UI copy)
