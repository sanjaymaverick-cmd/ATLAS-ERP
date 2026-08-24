# Command — CEO / Project Director surface

**Seats:** Atlas Developer Admin (`md@`), Atlas Project Director.  
**Not for:** Channel Agent / Admin, Site, Stores (no full money board).

Locked map: Group A — Today → **Command**. Portfolio is the cross-project open-items / heat-map detail layer. This is not a separate BI product.

## Principles

| Principle | Rule |
|---|---|
| One system | Frappe Desk page(s) inside `erpatlas`. Reads ERPNext Accounts + Atlas DocTypes. No parallel Tableau app. |
| Role-adapted | MD: all Legal Entities they may see. PD: assigned projects. Finance: money strips. Site: never cash KPIs. |
| Exception-first | Red/amber and “Waiting for a yes” drive the day. Green totals are secondary. |
| Books = truth | Cash, AR, AP, commission liability from GL / SO / PE / JE — not shadow totals. |
| AI is assistive | Predictions and risk scores **advise only**. Never auto-hold, auto-pay, or auto-approve. |
| Explainable | Every risk/forecast shows drivers. No opaque “risk = 72”. |

## Layout (single Command page)

```
Filters: Legal Entity | Project | date range (default trailing 30d + YTD)

KPI strip: Cash & runway | Sales velocity | Collection health | Approvals aging
Risk radar (top 5) | Pipeline & inventory (Available / Held / Booked / Sold)
AI outlook (30/90d) — revenue, cash, slippage (read-only)
Portfolio heat map (projects × health)
Exception queue (Approvals + site + commercial + docs when those modules exist)
```

Drill-through: KPI → filtered list → DocType form.

## KPI set (v1)

### Money (ERPNext Accounts)

- Cash position (bank + cash GL)
- Runway / net burn (cash ÷ 3-month avg net outflow)
- Collections MTD / QTD (PE linked to Booking / SO)
- Receivables plan vs actual (unpaid steps + SO schedule)
- Payables (supplier + commission payable accrued)
- Gross booking value MTD (Σ Active Booking consideration)
- Revenue recognized (submitted SI)
- Commission liability (Accrued / Approved, not Paid)
- Project spend (PO / PE by project)

### Sales & inventory (Atlas Unit / Hold / Booking)

- Units by status counts
- Hold conversion %, avg days on hold
- Channel vs in-house mix
- Funnel when Lead module exists

### Delivery (when Handover/Site exist)

- Possession-ready count (OC + snags + plan collected)
- Open snags aging, diary gaps, NCR overdue, vendor Active %

### Governance

- Approvals pending / past SLA
- Four-eyes grants pending
- Owner decisions open

## Risk domains

1. Liquidity — collection lag, PE concentration, cash vs 30d payables  
2. Sales — Held without book, expired holds, channel concentration  
3. Delivery — OC delay, snag backlog, possession blocked  
4. Commercial — PO without Active vendor, cost variance  
5. Compliance — GST template post-OC, TDS on commission PI (CA-configured)  
6. Approval stall — money kinds pending > N days  

**Card shape:** severity, driver text, linked docs, suggested Waiting On. No auto-action.

Start with **deterministic thresholds** in Atlas Settings. ML scores may layer later without changing the card UI.

## AI analytics & predictions

| Capability | Notes |
|---|---|
| Sales forecast 30/90d | Model on weekly bookings by project/tower |
| Collection forecast | Step slippage |
| Hold→Book probability | Open holds |
| Possession delay risk | Snags, OC, collection % |
| Anomaly detection | KPI spikes/drops |
| Narrative brief | LLM over **structured KPI JSON only** |
| What-if | Sandbox calc only — never posts |

**Hard rules**

- Assistant stays draft-only for actions.
- Predictions never write Unit status, Payment Entry, or Approval decisions.
- External scoring OK (same pattern as CatBoost).
- Store as-of, model id, feature summary on every snapshot for audit.

## Implementation (ERPNext v16)

| Layer | Build |
|---|---|
| UI | Custom Page `command` + Workspace Number Cards / charts |
| Aggregates | Optional daily `Atlas KPI Snapshot` for speed |
| Risk | Pure rules module first (`command/risk.py`); no frappe in pure tests |
| Permissions | Developer Admin + Project Director; Legal Entity / Project filters |
| Settings | SLA days, risk thresholds, target toggles on Atlas Settings |

## Phases

| Phase | Scope |
|---|---|
| **P0** | Command page shell + live counts (units, holds, approvals aging) + exception list from Atlas Approval |
| **P1** | Money/sales KPIs after Atlas Booking + SO/PE path |
| **P2** | Deterministic risk cards + Atlas Settings thresholds |
| **P3** | Daily KPI Snapshot, sparklines, portfolio heat map |
| **P4** | Predictions + narrative brief from KPI JSON |
| **P5** | Board-pack PDF snapshot |

P0 does not require Booking. P1+ does.

**P1:** Wired from Atlas Booking + payment steps + Payment Entry (`atlas_booking`) + Atlas Commission. Collections MTD, live/MTD booking value, plan vs actual, commission Accrued/Approved (not Paid). Hold→book % and channel vs in-house mix. Bank cash and runway are still not on this page (need GL; not a shadow ledger).

## Out of scope for Command code

- Rebuilding Atlas Booking, Handover, or CatBoost inside this page
- Auto-approving or auto-paying from a dashboard click
- Channel seats seeing MD cash KPIs
