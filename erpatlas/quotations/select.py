"""Compare supplier quotes and pick a winner. No frappe. No PO until vendor Active."""

from __future__ import annotations

from typing import Iterable, Mapping

from erpatlas.books.payment_gst import money
from erpatlas.commercial.vendor import VENDOR_ACTIVE, refuse_purchase_order


def refuse_compare(quotes: Iterable[Mapping]) -> str | None:
	rows = list(quotes)
	if not rows:
		return "Need at least one supplier quote."
	return None


def rank_quotes(quotes: Iterable[Mapping]) -> list[dict]:
	rows = [dict(q) for q in quotes]
	return sorted(rows, key=lambda q: (money(q.get("amount") or 0), q.get("supplier") or ""))


def select_winner(quotes: Iterable[Mapping]) -> dict | None:
	ranked = rank_quotes(quotes)
	return ranked[0] if ranked else None


def refuse_award(*, winner: Mapping | None, vendor_stage: str | None) -> str | None:
	if not winner:
		return "Need at least one supplier quote."
	return refuse_purchase_order(atlas_stage=vendor_stage)


def award_plan(quotes: Iterable[Mapping], *, stages: Mapping[str, str | None]) -> dict:
	err = refuse_compare(quotes)
	if err:
		return {"error": err, "creates_payment_entry": False}
	winner = select_winner(quotes)
	stage = stages.get((winner or {}).get("supplier") or "")
	blocked = refuse_award(winner=winner, vendor_stage=stage)
	if blocked:
		return {"error": blocked, "winner": winner, "creates_payment_entry": False}
	return {
		"winner": winner,
		"ranked": rank_quotes(quotes),
		"creates_payment_entry": False,
		"next": "Purchase Order",
	}
