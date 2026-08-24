"""Stop Payment Entry from being used as a silent commission payout."""

from __future__ import annotations


def refuse_commission_auto_pay(doc, method=None):
	# Commission payouts are raised as Atlas Approval kind "Commission".
	# A Payment Entry is allowed only after that approval — Collections module
	# will set flags.in_atlas_commission_payout when it is the one creating it.
	import frappe

	if getattr(frappe.flags, "in_atlas_commission_payout", False):
		return
	ref = (doc.get("remarks") or "") + " " + (doc.get("reference_no") or "")
	if "commission" in ref.lower() and not doc.get("atlas_approval"):
		frappe.throw(
			"Commission is accrued only. Send it through Approvals; do not create a Payment Entry from here."
		)
