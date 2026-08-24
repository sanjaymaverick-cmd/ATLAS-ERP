import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today

from erpatlas.channel.adapter import bind_channel_company
from erpatlas.channel.report import refuse_second_report, report_key


class AtlasDailyReport(Document):
	def validate(self):
		if not self.report_date:
			self.report_date = today()
		bind_channel_company(self)
		self.report_key = report_key(agent=self.agent, report_date=str(self.report_date))
		if self.is_new():
			exists = frappe.db.exists("Atlas Daily Report", {"report_key": self.report_key})
			err = refuse_second_report(already_filed_today=bool(exists))
			if err:
				frappe.throw(_(err))
