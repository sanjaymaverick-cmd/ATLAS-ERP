import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.capital.gates import refuse_amount, refuse_split


class AtlasFundingSanction(Document):
	def validate(self):
		err = refuse_split(loan_pct=self.loan_pct, equity_pct=self.equity_pct)
		if err:
			frappe.throw(_(err))
		err = refuse_amount(amount=self.amount)
		if err:
			frappe.throw(_(err))
