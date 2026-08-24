"""Channel agent roster. User Permission is created at runtime — not a fixture."""

from __future__ import annotations


def refuse_bind(*, user: str | None, channel_company: str | None) -> str | None:
	if not (user or "").strip():
		return "Agent needs a User."
	if not (channel_company or "").strip():
		return "Agent needs a Channel Company."
	return None
