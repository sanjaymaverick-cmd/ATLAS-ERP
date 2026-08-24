from erpatlas.command.risk import RED, RISK_LIMIT, risk_cards


def test_risk_cards_never_auto_act():
	cards = risk_cards(
		holds=[{"name": "AHD-1", "status": "Held", "creation": "2026-08-01", "project": "Lake"}],
		approvals=[
			{
				"name": "AAP-1",
				"status": "Pending",
				"kind": "Hold booking",
				"aging_days": 9,
				"title": "Hold → book",
				"waiting_on": "Sales Manager / MD",
			}
		],
		bookings=[],
		money_board={"plan_gross": "100", "receivable": "80"},
		today="2026-08-24",
	)
	assert cards
	assert all(c["auto_action"] is False for c in cards)
	assert cards[0]["severity"] == RED


def test_approval_stall_only_money_kinds_past_sla():
	cards = risk_cards(
		holds=[],
		approvals=[
			{"name": "AAP-m", "status": "Pending", "kind": "Commission", "aging_days": 4, "title": "Payout"},
			{"name": "AAP-v", "status": "Pending", "kind": "Vendor", "aging_days": 40, "title": "Vendor"},
			{"name": "AAP-done", "status": "Approved", "kind": "Commission", "aging_days": 40},
		],
		bookings=[],
		money_board={},
		today="2026-08-24",
		thresholds={"approval_sla_days": 3},
	)
	stall = [c for c in cards if c["domain"] == "Approval stall"]
	assert len(stall) == 1
	assert stall[0]["refs"] == ["AAP-m"]
	assert stall[0]["auto_action"] is False


def test_held_without_book_and_expiring():
	cards = risk_cards(
		holds=[
			{"name": "AHD-old", "status": "Held", "creation": "2026-08-01", "until": "2026-08-30"},
			{"name": "AHD-soon", "status": "Held", "creation": "2026-08-23", "until": "2026-08-24"},
			{"name": "AHD-x", "status": "Expired", "until": "2026-08-20"},
		],
		approvals=[],
		bookings=[],
		money_board={},
		today="2026-08-24",
		thresholds={"hold_without_book_days": 7, "hold_expiring_days": 2},
	)
	domains = [c["title"] for c in cards]
	assert any("held without a booking" in t for t in domains)
	assert any("expiring" in t for t in domains)
	assert any("expired" in t for t in domains)


def test_channel_concentration_and_collection_lag_thresholds():
	cards = risk_cards(
		holds=[],
		approvals=[],
		bookings=[
			{"name": "ABK-1", "status": "Active", "channel_company": "Pink City"},
			{"name": "ABK-2", "status": "Active", "channel_company": "Pink City"},
			{"name": "ABK-3", "status": "Active", "channel_company": ""},
		],
		money_board={"plan_gross": "1000", "receivable": "400"},
		today="2026-08-24",
		thresholds={"channel_concentration_percent": 60, "collection_lag_percent": 20},
	)
	assert any(c["domain"] == "Sales" and "Channel mix" in c["title"] for c in cards)
	lag = [c for c in cards if c["domain"] == "Liquidity"]
	assert lag and lag[0]["severity"] == "amber"


def test_delivery_and_vendor_cards_and_cap():
	cards = risk_cards(
		holds=[],
		approvals=[],
		bookings=[],
		money_board={},
		handovers=[
			{
				"name": "AHO-1",
				"status": "Snagging",
				"occupancy_certificate": "Pending",
			}
		],
		snags=[{"name": "ASG-1", "status": "Open"}],
		vendors=[{"name": "SUP-1", "atlas_stage": "Draft"}],
		today="2026-08-24",
	)
	assert any(c["domain"] == "Delivery" and "snag" in c["title"] for c in cards)
	assert any("Occupancy Certificate" in c["title"] for c in cards)
	assert any(c["domain"] == "Commercial" for c in cards)
	assert len(cards) <= RISK_LIMIT
	assert all(c["auto_action"] is False for c in cards)
