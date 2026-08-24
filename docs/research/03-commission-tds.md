# 03 — Commission accounts + TDS

**Invariant:** Commission **accrues** at Booking. Status starts Accrued. Approvals may mark Approved. **Nothing in Approvals or Commission creates a Payment Entry.**

## Parties

| Who earned it | Books party | Why |
|---|---|---|
| Channel Company | ERPNext **Supplier** (link on `Atlas Channel Company.supplier`) | Agency is a vendor. Purchase Invoice + TDS |
| Named Channel Agent (same firm) | Same Supplier (internal split is not books) | Do not pay the agent from Company bank unless they are a separate Supplier |
| In-house sales | Employee / payroll, or no PI | Accrual may still exist for reporting; payout is payroll or a separate PI |

Create the Supplier when the Channel Company is activated, not at first booking.

## Status vs books

| Commission status | Books | Payment Entry? |
|---|---|---|
| Accrued | Optional **Journal Entry**: Dr Commission Expense / Cr Commission Payable | No |
| Pending Payout Approval | Atlas Approval kind `Commission` | No |
| Approved for Payout | Still payable | No |
| Paid | **Purchase Invoice** (or Employee payment) then **Payment Entry** created by Finance from the PI | Yes, only here |
| Rejected / Cancelled / Written Off | Reverse the JE if posted | No |

v1 recommendation: **post the accrual JE on Booking submit** (expense in the period of sale). Payout is a later PI against the same Supplier, net of TDS, then Payment Entry.

If Finance prefers not to accrue until Approved, set Atlas Settings `accrue_commission_on` = `Booking` \| `Approval`. Default **Booking** (matches Atlas-3 “accrues on convert”).

## TDS (India) — configure, do not hardcode

Research snapshot 2026 (confirm with CA):

- Old **s.194H** commission/brokerage TDS: rate **2%** from 1 Oct 2024 (was 5%).
- Threshold: historically ₹15,000 / FY; some 2026 write-ups cite ₹20,000. **Put the number on Tax Withholding Category, not in Python.**
- Deduct on **credit or payment, whichever is earlier**. Accrual JE *can* create a TDS obligation — CA must choose whether TDS fires at Accrued or at PI/payment.
- GST on the agency invoice (18% typical) is separate. TDS is usually on the **taxable value excluding GST** (confirm).

**ERPNext v16 mechanism:** [Tax Withholding Category](https://docs.frappe.io/erpnext/tax-withholding-category)

1. Category e.g. `TDS 194H Commission`.
2. Rate rows with From/To dates (so 5% history and 2% current can coexist).
3. Transaction + cumulative thresholds.
4. Account Head = TDS Payable (liability).
5. Assign category on the **Supplier**.
6. On **Purchase Invoice**, “Consider for Tax Withholding”.
7. On **Payment Entry** of type Pay / Supplier, same checkbox for advances — ERPNext avoids double deduction when the PI later allocates the advance.

Do **not** implement TDS inside `Atlas Commission`. Let ERPNext compute it when Finance raises the PI.

## Chart of accounts (per Legal Entity)

| Account | Type | Used when |
|---|---|---|
| Commission Expense | Expense | Accrual JE and/or PI |
| Commission Payable | Liability | Accrual JE credit |
| TDS Payable (194H) | Liability | PI tax withholding |
| Bank | Asset | Payment Entry |

Cost Center / Project: tag the JE and PI with the Booking’s Project so P&L is per development.

## Duplicate approval

One pending Atlas Approval per Commission (already in Approvals design). Handler sets Commission → Approved for Payout. Handler **must not** call `frappe.get_doc("Payment Entry")`.

`erpatlas.approvals.guards.refuse_commission_auto_pay` already hooks Payment Entry validate — keep it: refuse PE that references a Commission DocType as voucher, or a custom flag `atlas_commission`. Legal path is PE against Purchase Invoice / Journal Entry only.

## GST on commission (agency)

Channel raises a GST invoice on the developer (RCM vs forward charge — CA). ERPNext Purchase Taxes and Charges template on the PI. Unrelated to GST on the **unit sale** (note 02).
