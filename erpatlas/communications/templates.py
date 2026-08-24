"""WhatsApp template registry. No send. No frappe."""

from __future__ import annotations

CATEGORIES = ("utility", "marketing")
STATUSES = ("draft", "pending", "approved", "paused")


def refuse_send() -> str:
	return "Templates are registered only. Sending WhatsApp is not enabled in this slice."


def refuse_register(*, name: str | None, body: str | None) -> str | None:
	if not (name or "").strip():
		return "Template needs a name."
	if not (body or "").strip():
		return "Template needs a body."
	return None
