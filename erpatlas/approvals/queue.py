"""Unified approval queue. Callers pass roles and facts; this module decides who may act.

Handlers for side effects live in owning modules and are registered by kind.
Do not import frappe here.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Iterable

WAITING_ON = (
	"Managing Director",
	"Project Director",
	"Finance Lead",
	"Sales Manager",
	"Sales Manager / MD",
	"Four-eyes approver",
)

WAITING_ON_ROLES: dict[str, frozenset[str]] = {
	"Managing Director": frozenset({"Atlas Developer Admin"}),
	"Project Director": frozenset({"Atlas Project Director"}),
	"Finance Lead": frozenset({"Atlas Finance"}),
	"Sales Manager": frozenset({"Atlas Sales Manager"}),
	"Sales Manager / MD": frozenset({"Atlas Sales Manager", "Atlas Developer Admin"}),
	"Four-eyes approver": frozenset({"Atlas Developer Admin", "Atlas Project Director"}),
}

DECIDER_ROLES = frozenset(
	{
		"Atlas Developer Admin",
		"Atlas Project Director",
		"Atlas Finance",
		"Atlas Sales Manager",
	}
)

KINDS = (
	"Purchase order",
	"Vendor",
	"Document export",
	"Change",
	"Commission",
	"Hold booking",
	"Payment",
)

MONEY_KINDS = frozenset({"Purchase order", "Commission", "Hold booking", "Payment"})
CHANGE_MONEY_IF_AMOUNT = "Change"

PENDING = "Pending"
APPROVED = "Approved"
REJECTED = "Rejected"
DECISIONS = (APPROVED, REJECTED)

Handler = Callable[[dict, str], str | None]
HANDLERS: dict[str, Handler] = {}


def register_handler(kind: str, handler: Handler) -> None:
	if kind not in KINDS:
		raise ValueError(f"Unknown approval kind {kind}")
	HANDLERS[kind] = handler


def waiter_roles_are_complete() -> bool:
	return set(WAITING_ON) == set(WAITING_ON_ROLES)


def can_act_on_approval(roles: Iterable[str], waiting_on: str, md_bypass: bool) -> bool:
	role_set = set(roles)
	if not role_set & DECIDER_ROLES:
		return False
	if md_bypass and "Atlas Developer Admin" in role_set:
		return True
	mapped = WAITING_ON_ROLES.get(waiting_on)
	if not mapped:
		return False
	return bool(role_set & mapped)


def refuse_raise(*, kind: str, waiting_on: str, amount: float | None) -> str | None:
	if kind not in KINDS:
		return f"Unknown approval kind {kind}."
	if waiting_on not in WAITING_ON:
		return f"Unknown waiter {waiting_on}."
	if kind in MONEY_KINDS and amount is None:
		return f"{kind} cards need an amount."
	return None


def refuse_self_approve(*, kind: str, requested_by: str | None, actor: str | None) -> str | None:
	"""Original export is two people. MD bypass does not let the requester approve their own grant."""
	if kind != "Document export":
		return None
	if requested_by and actor and requested_by == actor:
		return "Four-eyes: the person who asked cannot approve this export."
	return None


def refuse_decide(
	*,
	status: str,
	decision: str,
	roles: Iterable[str],
	waiting_on: str,
	md_bypass: bool,
	kind: str = "",
	requested_by: str | None = None,
	actor: str | None = None,
) -> str | None:
	if status != PENDING:
		return "This item is already decided."
	if decision not in DECISIONS:
		return f"Decision must be {APPROVED} or {REJECTED}."
	if not can_act_on_approval(roles, waiting_on, md_bypass):
		return f"Waiting on {waiting_on}."
	if decision == APPROVED:
		self_err = refuse_self_approve(kind=kind, requested_by=requested_by, actor=actor)
		if self_err:
			return self_err
	return None


def run_handler(approval: dict, decision: str) -> str | None:
	handler = HANDLERS.get(approval.get("kind") or "")
	if not handler:
		return None
	return handler(approval, decision)
