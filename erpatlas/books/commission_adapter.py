"""Post commission Journal Entry / Purchase Invoice. Never a Payment Entry."""

from __future__ import annotations

import frappe
from frappe import _

from erpatlas.books.commission import (
	accrual_journal_accounts,
	accrual_journal_lines,
	refuse_payout_invoice,
	should_post_accrual_je,
)


def post_accrual_journal(commission) -> str | None:
	settings = frappe.get_single("Atlas Settings")
	accrue_on = getattr(settings, "accrue_commission_on", None) or "Booking"
	if not should_post_accrual_je(accrue_on=accrue_on, status=commission.status):
		return None
	expense = getattr(settings, "commission_expense_account", None)
	payable = getattr(settings, "commission_payable_account", None)
	err = accrual_journal_accounts(expense_account=expense, payable_account=payable)
	if err:
		return None
	company = frappe.db.get_value("Project", commission.project, "company")
	if not company:
		return None
	lines = accrual_journal_lines(
		amount=commission.amount,
		expense_account=expense,
		payable_account=payable,
		project=commission.project,
	)
	je = frappe.get_doc(
		{
			"doctype": "Journal Entry",
			"company": company,
			"posting_date": frappe.utils.today(),
			"user_remark": f"Atlas Commission {commission.name} accrual. Not a Payment Entry.",
			"accounts": [
				{
					"account": row["account"],
					"debit_in_account_currency": float(row["debit_in_account_currency"]),
					"credit_in_account_currency": float(row["credit_in_account_currency"]),
					"project": row["project"],
				}
				for row in lines
			],
		}
	)
	je.flags.ignore_permissions = True
	je.insert()
	je.submit()
	commission.db_set("journal_entry", je.name)
	return je.name


def raise_purchase_invoice(commission_name: str) -> dict:
	doc = frappe.get_doc("Atlas Commission", commission_name)
	supplier = frappe.db.get_value("Atlas Channel Company", doc.channel_company, "supplier")
	err = refuse_payout_invoice(status=doc.status, supplier=supplier)
	if err:
		frappe.throw(_(err))
	company = frappe.db.get_value("Project", doc.project, "company")
	if not company:
		frappe.throw(_("Project has no Legal Entity (Company)."))
	item = _commission_item()
	pi = frappe.get_doc(
		{
			"doctype": "Purchase Invoice",
			"company": company,
			"supplier": supplier,
			"project": doc.project,
			"apply_tds": 1,
			"items": [
				{
					"item_code": item,
					"qty": 1,
					"rate": float(doc.amount),
					"description": f"Atlas Commission {doc.name}",
				}
			],
		}
	)
	if hasattr(pi, "atlas_commission"):
		pi.atlas_commission = doc.name
	pi.flags.ignore_permissions = True
	pi.insert()
	return {"purchase_invoice": pi.name, "creates_payment_entry": False}


def _commission_item() -> str:
	code = "ATLAS-COMMISSION"
	if frappe.db.exists("Item", code):
		return code
	group = "All Item Groups"
	for candidate in ("Services", "All Item Groups"):
		if frappe.db.exists("Item Group", candidate):
			group = candidate
			break
	uom = "Nos" if frappe.db.exists("UOM", "Nos") else frappe.db.get_value("UOM", {})
	frappe.get_doc(
		{
			"doctype": "Item",
			"item_code": code,
			"item_name": "Channel commission",
			"item_group": group,
			"stock_uom": uom or "Nos",
			"is_stock_item": 0,
			"is_purchase_item": 1,
			"is_sales_item": 0,
		}
	).insert(ignore_permissions=True)
	return code
