import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today

from erpatlas.site.gates import diary_key, refuse_diary


class AtlasSiteDiary(Document):
	def validate(self):
		if not self.diary_date:
			self.diary_date = today()
		if not self.device_key:
			self.device_key = frappe.session.user
		if not self.author:
			self.author = frappe.session.user
		self.seal_key = diary_key(
			project=self.project, diary_date=str(self.diary_date), device_key=self.device_key
		)
		if self.is_new():
			exists = frappe.db.exists("Atlas Site Diary", {"seal_key": self.seal_key})
			err = refuse_diary(already_sealed=bool(exists))
			if err:
				frappe.throw(_(err))
