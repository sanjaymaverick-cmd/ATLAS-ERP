"""Append-only audit facts. No frappe. Never a Payment Entry."""

from __future__ import annotations


def refuse_edit() -> str:
	return "Audit events are append-only."


def event(*, actor: str, action: str, entity: str, ref: str | None = None) -> dict:
	return {
		"actor": actor,
		"action": action,
		"entity": entity,
		"ref": ref,
		"creates_payment_entry": False,
	}
