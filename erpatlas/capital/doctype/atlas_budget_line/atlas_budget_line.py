import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.capital.budget import refuse_amounts, remaining


class AtlasBudgetLine(Document):
	def validate(self):
		err = refuse_amounts(budget=self.budget, committed=self.committed)
		if err:
			frappe.throw(_(err))
		self.remaining = float(remaining(budget=self.budget, committed=self.committed))
