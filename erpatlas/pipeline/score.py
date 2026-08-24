"""Lead scoring. CatBoost is external (cat_features). No Ordered Target Statistics."""

from __future__ import annotations

from typing import Mapping

CAT_FEATURES = ("source", "stage", "kind")

HOT = "hot"
WARM = "warm"
COOL = "cool"


def band_for(score) -> str:
	s = float(score)
	if s >= 70:
		return HOT
	if s >= 40:
		return WARM
	return COOL


def catboost_payload(
	*,
	source: str | None,
	stage: str | None,
	kind: str | None,
	budget=0,
	unit_price=0,
	wa: int = 0,
	call: int = 0,
	brochure: int = 0,
	visit: int = 0,
) -> dict:
	"""Payload for the external scorer. categoricals stay raw — never target-encoded here."""
	return {
		"cat_features": list(CAT_FEATURES),
		"categoricals": {
			"source": source or "unknown",
			"stage": stage or "inquiry",
			"kind": kind or "flat",
		},
		"numerics": {
			"budget": float(budget or 0),
			"unit_price": float(unit_price or 0),
			"wa": int(wa or 0),
			"call": int(call or 0),
			"brochure": int(brochure or 0),
			"visit": int(visit or 0),
		},
	}


def hybrid_score(*, source: str | None, stage: str | None, budget=0, unit_price=0) -> dict:
	"""Local fallback. Not CatBoost. Not Ordered Target Statistics."""
	score = 20
	if (source or "") in ("walk-in", "website", "partner"):
		score += 20
	if (stage or "") in ("qualified", "visit", "negotiation", "documentation"):
		score += 20
	price = float(unit_price or 0)
	bud = float(budget or 0)
	if price and bud and abs(bud - price) / price <= 0.2:
		score += 25
	elif bud >= 5_000_000:
		score += 10
	score = min(100, score)
	return {
		"score": score,
		"band": band_for(score),
		"served_by": "hybrid",
		"model": "hybrid",
		"reasons": ["Local hybrid fallback — CatBoost is an external scorer."],
	}


def apply_external_score(payload: Mapping, body: Mapping) -> dict:
	score = float(body.get("score") or 0)
	return {
		"score": score,
		"band": body.get("band") or band_for(score),
		"served_by": "catboost",
		"model": body.get("model") or "catboost",
		"reasons": list(body.get("reasons") or ["External CatBoost scorer."]),
		"request": dict(payload),
	}
