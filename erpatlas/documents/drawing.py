"""Drawing register. No viewer. Not a controlled original (four-eyes lives on Atlas Controlled Document)."""

from __future__ import annotations

KINDS = ("master", "floor", "structural", "mep", "other")
DRAFT = "draft"
IFC = "ifc"
AS_BUILT = "as-built"
DRAWING_STATUSES = (DRAFT, IFC, AS_BUILT)


def refuse_register(*, title: str | None) -> str | None:
	if not str(title or "").strip():
		return "Title required."
	return None
