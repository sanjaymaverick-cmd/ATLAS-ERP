from erpatlas.site.gates import FAIL, PASS, diary_key, ncr_from_fail, refuse_complete, refuse_diary


def test_one_diary_per_device_per_day():
	assert diary_key(project="Lake", diary_date="2026-08-24", device_key="phone-1") == "Lake::2026-08-24::phone-1"
	assert refuse_diary(already_sealed=False) is None
	assert "already exists" in refuse_diary(already_sealed=True)


def test_inspection_completes_once_pass_or_fail():
	assert refuse_complete(current="Pending", result=PASS) is None
	assert refuse_complete(current="Pending", result=FAIL) is None
	assert "already complete" in refuse_complete(current=PASS, result=FAIL)
	assert "Pass or Fail" in refuse_complete(current="Pending", result="maybe")


def test_fail_raises_ncr_not_a_payment():
	ncr = ncr_from_fail(template="Pour", location="L1")
	assert ncr["kind"] == "ncr"
	assert "Pour" in ncr["title"]
	assert ncr["raises_approval"] is False
