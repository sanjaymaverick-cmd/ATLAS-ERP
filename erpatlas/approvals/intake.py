"""Source modules raise an Atlas Approval through this function, never a raw insert with a made-up waiter."""

from __future__ import annotations

from erpatlas.approvals.queue import refuse_raise


def raise_approval(
	*,
	kind: str,
	title: str,
	project: str,
	waiting_on: str,
	amount: float | None = None,
	ref_doctype: str | None = None,
	ref_name: str | None = None,
	context: str | None = None,
) -> str:
	import frappe

	err = refuse_raise(kind=kind, waiting_on=waiting_on, amount=amount)
	if err:
		frappe.throw(err)
	if kind == "Commission" and ref_name:
		exists = frappe.db.exists(
			"Atlas Approval",
			{"kind": "Commission", "ref_name": ref_name, "status": "Pending"},
		)
		if exists:
			frappe.throw("This commission is already waiting in Approvals.")
	if kind == "Hold booking" and ref_name:
		exists = frappe.db.exists(
			"Atlas Approval",
			{"kind": "Hold booking", "ref_name": ref_name, "status": "Pending"},
		)
		if exists:
			frappe.throw("This hold is already waiting in Approvals.")
	doc = frappe.get_doc(
		{
			"doctype": "Atlas Approval",
			"kind": kind,
			"title": title,
			"project": project,
			"waiting_on": waiting_on,
			"amount": amount,
			"status": "Pending",
			"ref_doctype": ref_doctype,
			"ref_name": ref_name,
			"context": context,
			"requested_by": frappe.session.user,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name
