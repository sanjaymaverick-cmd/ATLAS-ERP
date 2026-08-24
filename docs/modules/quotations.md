# Quotations — RFQ → compare → select → PO

**ERPNext:** native Request for Quotation, Supplier Quotation, Purchase Order.

**Atlas rule:** no PO until the vendor is Active (GSTIN). Compare ranks lowest grand total among submitted quotes; award is refused if that supplier’s `atlas_stage` is not Active.

Whitelist: `erpatlas.quotations.award.award_lowest`

Does not create a Payment Entry.
