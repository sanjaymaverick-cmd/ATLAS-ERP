# Unified Atlas Approval DocType, not per-DocType ERPNext Workflow

Atlas-3 Approvals is one queue: Purchase order, Vendor, Document export, Change, Commission, Hold booking (and later Payment). Each card has kind, title, waiting-on, aging, amount, context, and Approve/Reject. ERPNext Workflow is per DocType, has no shared aging/amount card, and cannot route “Four-eyes approver” or “Sales Manager / MD” as a closed Waiting On list.

ERPATLAS keeps a custom **Atlas Approval** DocType as the product queue. Source modules raise a row; on decide, a registered handler in the owning module runs. ERPNext Workflow may still be used later as an extra submit/cancel gate on Purchase Order, but it is not the decision surface.

**Consequence:** `can_act_on_approval` is the only place Waiting On is mapped to roles. Adding a waiter without a role map is a hard error.
