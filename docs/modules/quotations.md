# Quotations — RFQ → compare → select → PO

**ERPNext:** native Request for Quotation, Supplier Quotation, Purchase Order.

**Atlas rule:** no PO until the vendor is Active (GSTIN). Compare ranks lowest grand total among submitted quotes; award is refused if that supplier’s `atlas_stage` is not Active.

Whitelist: `erpatlas.quotations.award.award_lowest`

A draft Purchase Order **Send for approval** raises kind `Purchase order`. Submit runs only after Approved. Does not create a Payment Entry.
