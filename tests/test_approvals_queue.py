"""Atlas-3 Approvals acceptance, as pure rules."""

from erpatlas.approvals.queue import (
	APPROVED,
	HANDLERS,
	PENDING,
	REJECTED,
	WAITING_ON,
	WAITING_ON_ROLES,
	can_act_on_approval,
	refuse_decide,
	refuse_raise,
	refuse_self_approve,
	register_handler,
	run_handler,
	waiter_roles_are_complete,
)


def test_every_waiter_has_roles():
	assert waiter_roles_are_complete()
	assert set(WAITING_ON) == set(WAITING_ON_ROLES)


def test_md_bypass_lets_developer_admin_act():
	assert can_act_on_approval(["Atlas Developer Admin"], "Project Director", md_bypass=True)
	assert not can_act_on_approval(["Atlas Developer Admin"], "Project Director", md_bypass=False)


def test_named_waiter_only():
	assert can_act_on_approval(["Atlas Sales Manager"], "Sales Manager / MD", md_bypass=False)
	assert can_act_on_approval(["Atlas Developer Admin"], "Sales Manager / MD", md_bypass=False)
	assert not can_act_on_approval(["Atlas Finance"], "Sales Manager / MD", md_bypass=False)
	assert not can_act_on_approval(["Atlas Channel Agent"], "Managing Director", md_bypass=True)


def test_four_eyes_maps_to_md_and_pd():
	assert can_act_on_approval(["Atlas Project Director"], "Four-eyes approver", md_bypass=False)
	assert can_act_on_approval(["Atlas Developer Admin"], "Four-eyes approver", md_bypass=False)
	assert not can_act_on_approval(["Atlas Documents"], "Four-eyes approver", md_bypass=False)


def test_money_kinds_need_amount():
	assert refuse_raise(kind="Commission", waiting_on="Managing Director", amount=None)
	assert refuse_raise(kind="Hold booking", waiting_on="Sales Manager / MD", amount=None)
	assert refuse_raise(kind="Purchase order", waiting_on="Managing Director", amount=None) is not None
	assert refuse_raise(kind="Hold booking", waiting_on="Sales Manager / MD", amount=0) is None
	assert refuse_raise(kind="Vendor", waiting_on="Managing Director", amount=None) is None


def test_unknown_kind_or_waiter_refused():
	assert refuse_raise(kind="Bonus", waiting_on="Managing Director", amount=1)
	assert refuse_raise(kind="Commission", waiting_on="Site Engineer", amount=1)


def test_cannot_decide_twice_or_without_seat():
	assert refuse_decide(
		status=APPROVED,
		decision=REJECTED,
		roles=["Atlas Developer Admin"],
		waiting_on="Managing Director",
		md_bypass=True,
	)
	assert refuse_decide(
		status=PENDING,
		decision=APPROVED,
		roles=["Atlas Channel Agent"],
		waiting_on="Managing Director",
		md_bypass=True,
	)
	assert (
		refuse_decide(
			status=PENDING,
			decision=APPROVED,
			roles=["Atlas Sales Manager"],
			waiting_on="Sales Manager / MD",
			md_bypass=False,
		)
		is None
	)


def test_handler_runs_before_status_would_flip():
	seen = []

	def boom(approval, decision):
		seen.append((approval["kind"], decision))
		return "Hold not active."

	register_handler("Hold booking", boom)
	try:
		err = run_handler({"kind": "Hold booking", "ref_name": "AHD-1"}, APPROVED)
		assert err == "Hold not active."
		assert seen == [("Hold booking", APPROVED)]
	finally:
		HANDLERS.pop("Hold booking", None)


def test_missing_handler_is_not_a_pay():
	assert run_handler({"kind": "Commission"}, APPROVED) is None


def test_export_requester_cannot_approve_own_grant():
	assert refuse_self_approve(
		kind="Document export", requested_by="docs@atlas.local", actor="docs@atlas.local"
	)
	assert (
		refuse_self_approve(
			kind="Document export", requested_by="docs@atlas.local", actor="md@atlas.local"
		)
		is None
	)
	assert (
		refuse_self_approve(kind="Purchase order", requested_by="cm@atlas.local", actor="cm@atlas.local")
		is None
	)
	assert refuse_decide(
		status=PENDING,
		decision=APPROVED,
		roles=["Atlas Developer Admin"],
		waiting_on="Four-eyes approver",
		md_bypass=True,
		kind="Document export",
		requested_by="md@atlas.local",
		actor="md@atlas.local",
	)
