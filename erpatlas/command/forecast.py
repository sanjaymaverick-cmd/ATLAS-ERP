"""Read-only forecasts from KPI snapshots. Not CatBoost. Never writes Unit, PE, or Approval."""

from __future__ import annotations

from typing import Iterable, Mapping

from erpatlas.books.payment_gst import money

MODEL_ID = "linear-snapshot"


def linear_outlook(points: Iterable, *, horizon_days: int) -> dict:
	series = [money(p) for p in points]
	if not series:
		projected = money(0)
		slope = money(0)
	elif len(series) == 1:
		projected = series[0]
		slope = money(0)
	else:
		span = len(series) - 1
		slope = money((series[-1] - series[0]) / span)
		projected = money(series[-1] + slope * horizon_days)
		if projected < 0:
			projected = money(0)
	return {
		"horizon_days": horizon_days,
		"projected": projected,
		"slope_per_snapshot": slope,
		"model_id": MODEL_ID,
		"served_by": MODEL_ID,
		"auto_action": False,
		"writes_unit": False,
		"creates_payment_entry": False,
		"decides_approval": False,
	}


def narrative_brief(board: Mapping) -> list[str]:
	"""Plain-language bullets from structured Command JSON only."""
	units = board.get("units") or {}
	money_board = board.get("money") or {}
	approvals = board.get("approvals") or {}
	risks = board.get("risk") or []
	lines = [
		f"Inventory: {units.get('Available') or 0} Available · {units.get('Held') or 0} Held · {units.get('Booked') or 0} Booked · {units.get('Sold') or 0} Sold.",
		f"Live booking value {money_board.get('booking_value_live') or 0}; receivable {money_board.get('receivable') or 0}.",
		f"Approvals pending {approvals.get('pending') or 0}; oldest {approvals.get('oldest_days') or 0}d.",
	]
	if risks:
		top = risks[0]
		lines.append(f"Top risk ({top.get('severity')}): {top.get('title')}.")
	else:
		lines.append("No risk cards in this filter.")
	lines.append("Advisory only — Command does not approve, pay, or change a unit.")
	return lines
