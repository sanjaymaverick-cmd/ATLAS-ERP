# Documents — four-eyes original export

**Atlas-3:** register → quarantine → clear → request export → Approvals (Four-eyes approver) → single-use grant → consume.

**Atlas Drawing** is a revision register (draft / IFC / as-built). No viewer. Not a four-eyes original — that stays on Atlas Controlled Document.

**ERPNext:** not Workflow (ADR 0003). Atlas Approval kind `Document export`. Custom **Atlas Controlled Document** and **Atlas Export Grant**.

## Acceptance

| Atlas-3 | ERPATLAS |
|---|---|
| Quarantine cannot export | `refuse_request_export` |
| One live grant (Pending or Granted) per file | same |
| Waiting on Four-eyes approver | `raise_approval(..., waiting_on="Four-eyes approver")` |
| Requester cannot approve (even MD bypass) | `refuse_self_approve` — already in `approvals.queue` |
| Approve → Granted; Reject → Rejected | handler `on_document_export` |
| Consume once | `refuse_consume`; Used is terminal |
| Not a Payment Entry | handler never posts money |

MD four-eyes bypass stays **on** for other kinds (ADR 0006). Export is the exception: two distinct people.

## Status

Document: Quarantine → Review → Issued (Approved / Superseded stored).  
Grant: Pending → Granted → Used, or Rejected / Expired.

## Whitelist

- `...atlas_controlled_document.request_export`
- `...atlas_controlled_document.clear_quarantine`
- `...atlas_controlled_document.issue`
- `...atlas_export_grant.consume`
