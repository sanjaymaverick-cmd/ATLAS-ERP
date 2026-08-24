"""Lead ingest, phone normalise, project-level dedup. No frappe."""

from __future__ import annotations

from typing import Iterable, Mapping

STAGES = (
	"inquiry",
	"contacted",
	"qualified",
	"visit",
	"negotiation",
	"documentation",
	"handover",
	"won",
	"lost",
	"nurture",
)

STAGE_LABEL = {
	"inquiry": "New",
	"contacted": "Called",
	"qualified": "Serious buyer",
	"visit": "Site visit",
	"negotiation": "Price talk",
	"documentation": "Papers",
	"handover": "Give keys",
	"won": "Booked",
	"lost": "Lost",
	"nurture": "Follow later",
}

STAGE_NEXT = {
	"inquiry": "contacted",
	"contacted": "qualified",
	"qualified": "visit",
	"visit": "negotiation",
	"negotiation": "documentation",
	"documentation": "handover",
	"handover": None,
	"won": None,
	"lost": None,
	"nurture": "inquiry",
}

OPEN_STAGES = frozenset(s for s in STAGES if s not in ("lost", "nurture"))


def normalize_phone(phone: str | None) -> str:
	return "".join((phone or "").split())


def live_phone_key(*, stage: str, project: str, phone: str, lead_name: str | None = None) -> str | None:
	"""Unique while the lead is open on that project; otherwise this lead's name."""
	if stage not in OPEN_STAGES:
		return lead_name
	phone_key = normalize_phone(phone)
	if not project or not phone_key:
		return lead_name
	return f"{project}::{phone_key}"


def find_duplicate(leads: Iterable[Mapping], *, phone: str, project: str) -> dict | None:
	key = live_phone_key(stage="inquiry", project=project, phone=phone)
	if not key:
		return None
	for row in leads:
		if row.get("atlas_live_phone") == key:
			return dict(row)
		row_key = live_phone_key(
			stage=row.get("atlas_stage") or "inquiry",
			project=row.get("atlas_project") or "",
			phone=row.get("mobile_no") or row.get("phone") or "",
			lead_name=row.get("name"),
		)
		if row_key == key:
			return dict(row)
	return None


def refuse_ingest(
	*,
	lead_name: str | None,
	phone: str | None,
	project: str | None,
	duplicate: Mapping | None,
) -> str | None:
	if not (lead_name or "").strip():
		return "Lead needs a name."
	if not normalize_phone(phone):
		return "Lead needs a phone."
	if not project:
		return "Lead needs a Project."
	if duplicate:
		stage = duplicate.get("atlas_stage") or duplicate.get("stage") or "inquiry"
		shown = duplicate.get("mobile_no") or duplicate.get("phone") or phone
		return f"Duplicate lead on {shown} — already {stage}."
	return None


def refuse_advance(*, stage: str) -> str | None:
	if stage not in STAGES:
		return f"Unknown pipeline stage {stage}."
	if STAGE_NEXT.get(stage) is None and stage != "nurture":
		return f"Cannot advance from {stage}."
	return None


def next_stage(stage: str) -> str | None:
	return STAGE_NEXT.get(stage)
