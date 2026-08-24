"""Export grant adapter. Four-eyes decide lives in Approvals."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import now_datetime

from erpatlas.documents.grant import (
	DOC_ISSUED,
	DOC_REVIEW,
	GRANT_USED,
	LIVE_GRANT,
	grant_status_on_decision,
	refuse_clear_quarantine,
	refuse_consume,
	refuse_issue,
	refuse_request_export,
)


def request_export(document_name: str) -> dict:
	doc = frappe.get_doc("Atlas Controlled Document", document_name)
	live = frappe.db.exists(
		"Atlas Export Grant",
		{"document": document_name, "status": ["in", list(LIVE_GRANT)]},
	)
	err = refuse_request_export(doc_status=doc.status, existing_live=bool(live))
	if err:
		frappe.throw(_(err))
	grant = frappe.get_doc(
		{
			"doctype": "Atlas Export Grant",
			"document": doc.name,
			"project": doc.project,
			"revision": doc.revision,
			"status": "Pending",
			"requested_by": frappe.session.user,
		}
	)
	grant.insert(ignore_permissions=True)
	from erpatlas.approvals.intake import raise_approval

	approval = raise_approval(
		kind="Document export",
		title=f"{doc.title} — original {doc.revision}",
		project=doc.project,
		waiting_on="Four-eyes approver",
		ref_doctype="Atlas Export Grant",
		ref_name=grant.name,
		context="Single-use original. Requester cannot approve.",
	)
	return {"grant": grant.name, "approval": approval, "status": grant.status}


def consume_export(grant_name: str) -> dict:
	grant = frappe.get_doc("Atlas Export Grant", grant_name)
	err = refuse_consume(grant_status=grant.status)
	if err:
		frappe.throw(_(err))
	grant.status = GRANT_USED
	grant.used_by = frappe.session.user
	grant.used_at = now_datetime()
	frappe.flags.in_atlas_grant = True
	try:
		grant.save(ignore_permissions=True)
	finally:
		frappe.flags.in_atlas_grant = False
	return {"grant": grant.name, "status": GRANT_USED, "single_use": True}


def clear_quarantine(document_name: str) -> dict:
	doc = frappe.get_doc("Atlas Controlled Document", document_name)
	err = refuse_clear_quarantine(status=doc.status)
	if err:
		frappe.throw(_(err))
	doc.status = DOC_REVIEW
	doc.save()
	return {"document": doc.name, "status": DOC_REVIEW}


def issue_document(document_name: str) -> dict:
	doc = frappe.get_doc("Atlas Controlled Document", document_name)
	err = refuse_issue(status=doc.status)
	if err:
		frappe.throw(_(err))
	doc.status = DOC_ISSUED
	doc.save()
	return {"document": doc.name, "status": DOC_ISSUED}


def apply_export_decision(grant_name: str, decision: str) -> str | None:
	grant = frappe.get_doc("Atlas Export Grant", grant_name)
	grant.status = grant_status_on_decision(decision)
	frappe.flags.in_atlas_grant = True
	try:
		grant.save(ignore_permissions=True)
	finally:
		frappe.flags.in_atlas_grant = False
	return None
