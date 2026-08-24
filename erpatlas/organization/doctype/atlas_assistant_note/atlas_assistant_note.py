import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.organization.assistant import DRAFT, refuse_execute, stamp_draft


class AtlasAssistantNote(Document):
	def validate(self):
		self.status = DRAFT

	def on_submit(self):
		frappe.throw(_(refuse_execute(status=self.status)))
