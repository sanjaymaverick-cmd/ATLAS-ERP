"""Parcel, diligence, and statutory obligation rules. No frappe. RERA 70/30 bank split is not here."""

from __future__ import annotations

from typing import Iterable, Mapping

from erpatlas.books.payment_gst import money

IDENTIFIED = "identified"
DILIGENCE = "diligence"
ACQUIRED = "acquired"
CLOSED = "closed"
PARCEL_STATUSES = (IDENTIFIED, DILIGENCE, ACQUIRED, CLOSED)

OPEN = "open"
CLEAR = "clear"
FLAGGED = "flagged"
DILIGENCE_STATUSES = (OPEN, CLEAR, FLAGGED)

STANDARD_DILIGENCE = (
	"Title search — 30 year",
	"Encumbrance certificate",
	"Conversion / CLU",
	"Mutation in revenue record",
	"Access road NOC",
)


def refuse_file(*, status: str) -> str | None:
	if status == "filed":
		return "This obligation is already filed."
	return None


def overdue(*, status: str, due: str, today: str) -> bool:
	if status == "filed":
		return False
	return bool(due) and due < today


def refuse_add_parcel(*, title: str | None, khasra: str | None) -> str | None:
	if not str(title or "").strip() or not str(khasra or "").strip():
		return "Name and khasra required."
	return None


def refuse_add_diligence(*, title: str | None, parcel_status: str | None) -> str | None:
	if not str(title or "").strip():
		return "Title required."
	if parcel_status == ACQUIRED:
		return "This parcel is already acquired."
	if parcel_status == CLOSED:
		return "This parcel is closed."
	return None


def refuse_set_diligence(*, status: str | None) -> str | None:
	if status not in DILIGENCE_STATUSES:
		return "Diligence is open, clear, or flagged."
	return None


def status_on_diligence(parcel_status: str | None) -> str:
	if parcel_status == IDENTIFIED:
		return DILIGENCE
	return parcel_status or IDENTIFIED


def open_or_flagged(items: Iterable[Mapping]) -> list[dict]:
	return [dict(row) for row in items if row.get("status") != CLEAR]


def pack_titles_to_add(existing_titles: Iterable[str]) -> list[str]:
	have = {str(t).strip().lower() for t in existing_titles if t}
	return [title for title in STANDARD_DILIGENCE if title.lower() not in have]


def refuse_start_pack(*, parcel_status: str | None, existing_titles: Iterable[str]) -> str | None:
	if parcel_status in (ACQUIRED, CLOSED):
		return "This parcel is already acquired."
	if not pack_titles_to_add(existing_titles):
		return "Standard title pack is already on this parcel."
	return None


def refuse_acquire(
	*,
	parcel_status: str | None,
	items: Iterable[Mapping],
	consideration,
	sale_deed_no: str | None,
) -> str | None:
	if parcel_status == ACQUIRED:
		return "This parcel is already acquired."
	if parcel_status == CLOSED:
		return "This parcel is closed."
	rows = list(items)
	if not rows:
		return "Open the title pack before acquisition."
	blocked = open_or_flagged(rows)
	if blocked:
		titles = ", ".join(str(row.get("title") or "untitled") for row in blocked)
		return f"All due-diligence items must be clear before acquisition. Open or flagged: {titles}."
	if money(consideration or 0) <= 0:
		return "Consideration (₹) is required to acquire the parcel."
	if not str(sale_deed_no or "").strip():
		return "Sale deed number is required to acquire the parcel."
	return None
