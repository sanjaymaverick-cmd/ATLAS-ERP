import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.books.cases import refuse_settle, settle_effects


class AtlasBooksCase(Document):
	def validate(self):
		if self.status in ("reconciled", "exception") and not frappe.flags.get("in_atlas_books_case"):
			before = None if self.is_new() else self.get_doc_before_save()
			if before and before.status != self.status:
				frappe.throw(_("Settle this case with Reconcile or Exception. Atlas never posts a voucher."))


@frappe.whitelist()
def settle(name: str, decision: str, note: str | None = None):
	doc = frappe.get_doc("Atlas Books Case", name)
	err = refuse_settle(status=doc.status, decision=decision, note=note or doc.note)
	if err:
		frappe.throw(_(err))
	effects = settle_effects(decision)
	doc.status = effects["status"]
	if note:
		doc.note = note
	frappe.flags.in_atlas_books_case = True
	try:
		doc.save()
	finally:
		frappe.flags.in_atlas_books_case = False
	return effects
