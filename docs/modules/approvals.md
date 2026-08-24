# Approvals — DocType design

**Atlas-3 sources:** `src/lib/types.ts` `Approval`, `src/lib/waiting-on.ts`, `src/lib/roles.ts` `canActOnApproval`, `src/lib/store.ts` `decideApproval`, `src/routes/app/approvals.tsx`, `docs/Atlas-3-UX-Spec.md` §4, `docs/decisions/four-eyes.md`.

**ERPNext:** not Workflow. See ADR 0003.

## Acceptance

| Atlas-3 criterion | ERPATLAS rule |
|---|---|
| One queue for every kind of request | Atlas Approval DocType |
| Approve/Reject only if this seat is the named waiter | `can_act_on_approval` |
| MD can act on any item (default) | Atlas Settings `md_bypass_four_eyes` = 1 (ADR 0006) |
| Money cards always show amount | validate: money kinds require amount |
| Approve and Reject both write audit | `track_changes` + comment / Version |
| Document export is four-eyes + single-use | kind `Document export`, waiting on Four-eyes approver; grant consumed elsewhere |
| Commission accrues; send-to-Approvals does not pay | kind `Commission`; handler sets Approved/Rejected; never Payment Entry |
| Duplicate commission Approval refused | one pending row per Commission |
| Partner hold → booking in this queue | kind `Hold booking`; unit stays Held |
| View-only seats see cards without actions | Desk permissions + `can_act` |

## Waiting On (closed list)

| Waiting On | Roles |
|---|---|
| Managing Director | Atlas Developer Admin |
| Project Director | Atlas Project Director |
| Finance Lead | Atlas Finance |
| Sales Manager | Atlas Sales Manager |
| Sales Manager / MD | Atlas Sales Manager, Atlas Developer Admin |
| Four-eyes approver | Atlas Developer Admin, Atlas Project Director |

Adding a value without a role map is a test failure (`WAITING_ON` × `WAITING_ON_ROLES` same keys).

Who may **decide** at all: Developer Admin, Project Director, Finance, Sales Manager. Channel seats never decide.

## Kinds

| Kind | Raised by | On Approved | On Rejected | Amount required |
|---|---|---|---|---|
| Purchase order | Commercial | PO → Approved / submitted | stays unapproved | yes |
| Vendor | Commercial | Supplier atlas stage → Active | stays at Approval | no |
| Document export | Documents | Export Grant → Granted | Grant → Rejected | no |
| Change | Change Control | VO → Approved | VO → Rejected | if money |
| Commission | Channel / Sales | Commission → Approved (still not paid) | Commission → Rejected | yes |
| Hold booking | Inventory | `bookHold` completes | clear `booking_requested` | yes |
| Payment | Collections (later) | then and only then a Payment Entry may be created | no payment | yes |

Handlers: Hold booking, Commission, Vendor, Document export, Change, **Payment** (`post_collect`), **Purchase order** (submit PO). Payment Entry is created only by the Payment handler.

## DocType: Atlas Approval

| Field | Type | Req | Notes |
|---|---|---|---|
| naming_series | Data | | `AAP-.#####` |
| kind | Select | yes | Closed list above |
| title | Data | yes | Human title on the card |
| project | Link → Project | yes | Entity filter via Project.company |
| amount | Currency | | Required for money kinds |
| waiting_on | Select | yes | Closed list |
| aging_days | Int | | Read-only, computed from creation |
| status | Select | yes | Pending / Approved / Rejected |
| ref_doctype | Link → DocType | | |
| ref_name | Dynamic Link | | |
| context | Small Text | | Vendor, quote line, “unit stays locked” |
| requested_by | Link → User | | Set on insert. Atlas-3 omitted this; four-eyes export needs it. |
| decided_by | Link → User | | Set on decide |
| decided_at | Datetime | | |

Cannot edit kind/ref after insert. Cannot decide twice.

## Status machine

```
Pending ──approve──► Approved
Pending ──reject───► Rejected
```

No reopen in this slice (Atlas-3 has none).

## Server rules

1. `raise_approval(...)` — source modules call this; they do not `insert` a raw row with a made-up waiter.
2. `decide(name, Approved|Rejected)` — load roles; `can_act_on_approval`; for Document export, requester ≠ approver (even if MD bypass is on); run handler; then set status. If the handler fails, status stays Pending.
3. Money kinds without amount → throw.
4. `md_bypass_four_eyes` read from Atlas Settings. Default true.
5. Desk list is the queue: filter Pending, sort by aging desc. Closed in a collapsed group (UX spec).

## Atlas Settings (Single)

| Field | Type | Default |
|---|---|---|
| md_bypass_four_eyes | Check | 1 |
| default_hold_days | Int | 7 |

## Whitelist

- `erpatlas.approvals.doctype.atlas_approval.atlas_approval.decide`
