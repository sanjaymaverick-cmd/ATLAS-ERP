"""Approval kind Payment: only Approved creates a Payment Entry."""

from __future__ import annotations

import json

from erpatlas.approvals.queue import APPROVED


def on_payment(approval: dict, decision: str) -> str | None:
	if decision != APPROVED:
		return None
	booking = approval.get("ref_name")
	if not booking:
		return "Payment has no booking."
	ctx = {}
	raw = approval.get("context") or ""
	if raw:
		try:
			ctx = json.loads(raw)
		except json.JSONDecodeError:
			ctx = {}
	amount = ctx.get("amount") or approval.get("amount")
	from erpatlas.booking.collect import post_collect

	try:
		post_collect(
			booking,
			amount,
			mode_of_payment=ctx.get("mode_of_payment") or None,
			approval_name=approval.get("name"),
		)
	except Exception as e:
		return str(e)
	return None
