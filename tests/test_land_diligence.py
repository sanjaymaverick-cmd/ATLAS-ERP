from erpatlas.land.gates import (
	ACQUIRED,
	CLEAR,
	DILIGENCE,
	FLAGGED,
	IDENTIFIED,
	OPEN,
	STANDARD_DILIGENCE,
	open_or_flagged,
	pack_titles_to_add,
	refuse_acquire,
	refuse_add_diligence,
	refuse_add_parcel,
	refuse_file,
	refuse_set_diligence,
	refuse_start_pack,
	status_on_diligence,
)


def test_parcel_needs_name_and_khasra():
	assert refuse_add_parcel(title="", khasra="41/2")
	assert refuse_add_parcel(title="Muhana Mandi", khasra="  ")
	assert refuse_add_parcel(title="Muhana Mandi", khasra="41/2") is None


def test_standard_pack_is_five_title_checks_and_skips_existing():
	assert len(STANDARD_DILIGENCE) == 5
	assert "Title search — 30 year" in STANDARD_DILIGENCE
	assert "Conversion / CLU" in STANDARD_DILIGENCE
	added = pack_titles_to_add(["Encumbrance certificate", "title search — 30 year"])
	assert added[0] == "Conversion / CLU"
	assert "Encumbrance certificate" not in added
	assert refuse_start_pack(parcel_status=IDENTIFIED, existing_titles=STANDARD_DILIGENCE)
	assert refuse_start_pack(parcel_status=ACQUIRED, existing_titles=[])
	assert refuse_start_pack(parcel_status=IDENTIFIED, existing_titles=[]) is None


def test_first_diligence_item_moves_identified_to_diligence():
	assert status_on_diligence(IDENTIFIED) == DILIGENCE
	assert status_on_diligence(DILIGENCE) == DILIGENCE
	assert status_on_diligence(ACQUIRED) == ACQUIRED
	assert refuse_add_diligence(title="", parcel_status=IDENTIFIED)
	assert refuse_add_diligence(title="Mutation", parcel_status=ACQUIRED)
	assert refuse_add_diligence(title="Mutation", parcel_status=IDENTIFIED) is None


def test_acquire_blocked_until_every_item_is_clear():
	open_item = {"title": "Title search — 30 year", "status": OPEN}
	flagged = {"title": "Conversion / CLU", "status": FLAGGED}
	clear = {"title": "Access road NOC", "status": CLEAR}
	assert "title pack" in refuse_acquire(
		parcel_status=IDENTIFIED, items=[], consideration="100", sale_deed_no="SD-1"
	)
	msg = refuse_acquire(
		parcel_status=DILIGENCE,
		items=[open_item, flagged, clear],
		consideration="100",
		sale_deed_no="SD-1",
	)
	assert "must be clear" in msg
	assert "Title search — 30 year" in msg
	assert "Conversion / CLU" in msg
	assert [r["title"] for r in open_or_flagged([open_item, flagged, clear])] == [
		"Title search — 30 year",
		"Conversion / CLU",
	]
	assert "Consideration" in refuse_acquire(
		parcel_status=DILIGENCE, items=[clear], consideration="0", sale_deed_no="SD-1"
	)
	assert "Sale deed" in refuse_acquire(
		parcel_status=DILIGENCE, items=[clear], consideration="10", sale_deed_no=""
	)
	assert (
		refuse_acquire(
			parcel_status=DILIGENCE, items=[clear], consideration="10", sale_deed_no="SD-1"
		)
		is None
	)
	assert refuse_acquire(
		parcel_status=ACQUIRED, items=[clear], consideration="10", sale_deed_no="SD-1"
	)


def test_diligence_statuses_and_obligation_file_unchanged():
	assert refuse_set_diligence(status="paid")
	assert refuse_set_diligence(status=CLEAR) is None
	assert refuse_file(status="filed")
