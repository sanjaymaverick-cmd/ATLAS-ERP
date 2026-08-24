"""Sales funnel and model monitor. No frappe. CatBoost stays an external scorer."""

from __future__ import annotations

from typing import Iterable, Mapping

from erpatlas.pipeline.ingest import STAGES
from erpatlas.pipeline.score import HOT, WARM

FUNNEL_STAGES = ("inquiry", "contacted", "qualified", "visit", "negotiation", "won")


def funnel_counts(leads: Iterable[Mapping]) -> list[dict]:
	rows = [dict(r) for r in leads]
	out = []
	for stage in FUNNEL_STAGES:
		out.append({"stage": stage, "count": sum(1 for r in rows if r.get("atlas_stage") == stage)})
	return out


def conversion_pct(leads: Iterable[Mapping]):
	rows = [dict(r) for r in leads]
	won = sum(1 for r in rows if r.get("atlas_stage") == "won")
	lost = sum(1 for r in rows if r.get("atlas_stage") == "lost")
	closed = won + lost
	if not closed:
		return None
	return round(won * 100 / closed, 2)


def band_mix(leads: Iterable[Mapping]) -> dict[str, int]:
	mix = {HOT: 0, WARM: 0, "cool": 0}
	for row in leads:
		band = row.get("atlas_band") or "cool"
		if band not in mix:
			band = "cool"
		mix[band] += 1
	return mix


def model_monitor(leads: Iterable[Mapping]) -> dict:
	"""Counts how scores were served. Does not run CatBoost or Ordered Target Statistics."""
	hybrid = 0
	external = 0
	for row in leads:
		served = str(row.get("atlas_score_model") or row.get("served_by") or "")
		if served == "catboost":
			external += 1
		elif served:
			hybrid += 1
	return {
		"hybrid": hybrid,
		"external_catboost": external,
		"served_by": "monitor",
		"reimplements_catboost": False,
		"ordered_target_statistics": False,
	}


def build_sales_analytics(leads: Iterable[Mapping]) -> dict:
	rows = [dict(r) for r in leads]
	return {
		"funnel": funnel_counts(rows),
		"conversion_pct": conversion_pct(rows),
		"bands": band_mix(rows),
		"monitor": model_monitor(rows),
		"open": sum(1 for r in rows if r.get("atlas_stage") in STAGES and r.get("atlas_stage") not in ("won", "lost", "nurture")),
		"auto_action": False,
		"creates_payment_entry": False,
		"writes_unit": False,
	}
