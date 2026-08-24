from erpatlas.pipeline.ingest import (
	find_duplicate,
	live_phone_key,
	next_stage,
	normalize_phone,
	refuse_advance,
	refuse_ingest,
)
from erpatlas.pipeline.permissions import lead_query_clause
from erpatlas.pipeline.score import CAT_FEATURES, catboost_payload, hybrid_score


def test_normalize_phone_strips_spaces():
	assert normalize_phone(" 98 100 12345 ") == "9810012345"


def test_duplicate_on_same_project_and_phone_unless_lost_or_nurture():
	open_row = {
		"name": "CRM-1",
		"atlas_stage": "inquiry",
		"atlas_project": "Lake",
		"mobile_no": "9810012345",
	}
	assert find_duplicate([open_row], phone="98 100 12345", project="Lake")["name"] == "CRM-1"
	lost = {**open_row, "atlas_stage": "lost", "name": "CRM-lost"}
	assert find_duplicate([lost], phone="9810012345", project="Lake") is None
	assert find_duplicate([open_row], phone="9810012345", project="Ridge") is None


def test_refuse_ingest_needs_name_phone_project_and_blocks_dup():
	assert "name" in refuse_ingest(lead_name="", phone="1", project="P", duplicate=None)
	assert "phone" in refuse_ingest(lead_name="Yadav", phone="", project="P", duplicate=None)
	assert "Project" in refuse_ingest(lead_name="Yadav", phone="1", project=None, duplicate=None)
	dup = {"mobile_no": "1", "atlas_stage": "contacted"}
	assert "Duplicate" in refuse_ingest(lead_name="Yadav", phone="1", project="P", duplicate=dup)
	assert refuse_ingest(lead_name="Yadav", phone="1", project="P", duplicate=None) is None


def test_live_phone_key_releases_lost_and_nurture():
	assert live_phone_key(stage="inquiry", project="Lake", phone="99", lead_name="L1") == "Lake::99"
	assert live_phone_key(stage="lost", project="Lake", phone="99", lead_name="L1") == "L1"
	assert live_phone_key(stage="nurture", project="Lake", phone="99", lead_name="L1") == "L1"


def test_advance_stops_at_won_lost_handover():
	assert next_stage("inquiry") == "contacted"
	assert refuse_advance(stage="won")
	assert refuse_advance(stage="lost")
	assert refuse_advance(stage="inquiry") is None


def test_catboost_payload_keeps_raw_categoricals_and_names_cat_features():
	payload = catboost_payload(source="99acres", stage="inquiry", kind="flat", budget=5_000_000)
	assert payload["cat_features"] == list(CAT_FEATURES)
	assert payload["categoricals"]["source"] == "99acres"
	assert "target" not in str(payload).lower()
	assert "ordered" not in str(payload).lower()


def test_channel_lead_query_is_own_company():
	assert "atlas_channel_company" in lead_query_clause("'Pink City'")
	assert lead_query_clause(None) == "1=0"


def test_hybrid_is_local_fallback_not_catboost():
	row = hybrid_score(source="walk-in", stage="visit", budget=10_000_000, unit_price=10_000_000)
	assert row["served_by"] == "hybrid"
	assert row["band"] in ("hot", "warm", "cool")
	assert "CatBoost" in row["reasons"][0]
