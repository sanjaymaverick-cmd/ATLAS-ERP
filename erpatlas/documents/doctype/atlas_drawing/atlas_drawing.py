import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.documents.drawing import refuse_register


class AtlasDrawing(Document):
	def validate(self):
		err = refuse_register(title=self.title)
		if err:
			frappe.throw(_(err))
		if not self.revision:
			self.revision = "R0"
