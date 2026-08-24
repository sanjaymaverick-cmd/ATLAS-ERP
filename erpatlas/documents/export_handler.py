"""Approval kind Document export: grant Granted or Rejected. Never a Payment Entry."""

from __future__ import annotations


def on_document_export(approval: dict, decision: str) -> str | None:
	name = approval.get("ref_name")
	if not name:
		return "Document export has no grant."
	from erpatlas.documents.adapter import apply_export_decision

	return apply_export_decision(name, decision)
