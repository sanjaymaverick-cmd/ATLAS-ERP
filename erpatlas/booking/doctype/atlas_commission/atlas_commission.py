import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.approvals.queue import PENDING


class AtlasCommission(Document):
	def validate(self):
		if self.is_new():
			return
		if frappe.flags.get("in_atlas_commission"):
			return
		before = self.get_doc_before_save()
		if before and before.status != self.status:
			frappe.throw(_("Commission status is locked. Send it through Approvals; never pay from here."))


@frappe.whitelist()
def send_to_approvals(name: str):
	doc = frappe.get_doc("Atlas Commission", name)
	if doc.status != "Accrued":
		frappe.throw(_("Only an Accrued commission can wait in Approvals."))
	from erpatlas.approvals.intake import raise_approval

	approval = raise_approval(
		kind="Commission",
		title=f"Commission · {doc.channel_company} · {doc.booking}",
		project=doc.project,
		waiting_on="Finance Lead",
		amount=float(doc.amount),
		ref_doctype="Atlas Commission",
		ref_name=doc.name,
		context="Accrued only. Approval does not create a Payment Entry.",
	)
	return {"approval": approval, "status": PENDING}
