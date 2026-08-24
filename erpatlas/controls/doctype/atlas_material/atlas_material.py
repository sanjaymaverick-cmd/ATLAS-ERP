import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.books.payment_gst import money
from erpatlas.controls.stock import refuse_issue, refuse_receive


class AtlasMaterial(Document):
	pass


@frappe.whitelist()
def receive(material: str, qty: float):
	err = refuse_receive(qty=qty)
	if err:
		frappe.throw(_(err))
	doc = frappe.get_doc("Atlas Material", material)
	doc.received = float(money(doc.received or 0) + money(qty))
	doc.save()
	return {"received": doc.received, "issued": doc.issued}


@frappe.whitelist()
def issue(material: str, qty: float):
	doc = frappe.get_doc("Atlas Material", material)
	err = refuse_issue(received=doc.received or 0, issued=doc.issued or 0, qty=qty)
	if err:
		frappe.throw(_(err))
	doc.issued = float(money(doc.issued or 0) + money(qty))
	doc.save()
	return {"received": doc.received, "issued": doc.issued}
