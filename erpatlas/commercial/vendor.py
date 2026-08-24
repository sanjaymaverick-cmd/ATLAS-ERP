"""Vendor Active gate. No frappe. GSTIN is required; rates are not."""

from __future__ import annotations

VENDOR_DRAFT = "Draft"
VENDOR_APPROVAL = "Approval"
VENDOR_ACTIVE = "Active"


def refuse_purchase_order(*, atlas_stage: str | None) -> str | None:
	if atlas_stage is None:
		return None
	if atlas_stage != VENDOR_ACTIVE:
		return "Purchase orders cannot be issued until the vendor is Active."
	return None


def refuse_vendor_active(*, gstin: str | None) -> str | None:
	if not (gstin or "").strip():
		return "GSTIN required before the vendor can be Active."
	return None
