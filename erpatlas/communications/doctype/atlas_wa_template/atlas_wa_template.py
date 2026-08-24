import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.communications.templates import refuse_register, refuse_send


class AtlasWaTemplate(Document):
	def validate(self):
		err = refuse_register(name=self.template_name, body=self.body)
		if err:
			frappe.throw(_(err))


@frappe.whitelist()
def send_template(name: str):
	frappe.throw(_(refuse_send()))
