"""Ingest and advance native ERPNext Lead. CatBoost HTTP is optional."""

from __future__ import annotations

import json
import urllib.request

import frappe
from frappe import _

from erpatlas.pipeline.ingest import (
	find_duplicate,
	live_phone_key,
	next_stage,
	normalize_phone,
	refuse_advance,
	refuse_ingest,
)
from erpatlas.pipeline.score import catboost_payload, hybrid_score, apply_external_score
from erpatlas.property_inventory.lock import CHANNEL_ROLES
from erpatlas.property_inventory.permissions import channel_company_for


@frappe.whitelist()
def ingest_lead(
	project: str,
	lead_name: str,
	phone: str,
	source: str | None = None,
	unit: str | None = None,
	budget=None,
	note: str | None = None,
	kind: str | None = None,
	channel_company: str | None = None,
):
	phone_key = normalize_phone(phone)
	open_leads = frappe.get_all(
		"Lead",
		filters={"atlas_project": project, "atlas_stage": ["not in", ["lost", "nurture"]]},
		fields=["name", "atlas_stage", "atlas_project", "mobile_no", "atlas_live_phone"],
	)
	dup = find_duplicate(open_leads, phone=phone_key, project=project)
	err = refuse_ingest(lead_name=lead_name, phone=phone, project=project, duplicate=dup)
	if err:
		frappe.throw(_(err))
	if set(frappe.get_roles()) & CHANNEL_ROLES:
		bound = channel_company_for(frappe.session.user)
		if not bound:
			frappe.throw(_("Channel seats must be bound to a Channel Company."))
		channel_company = bound
	unit_price = 0
	if unit:
		unit_price = frappe.db.get_value("Atlas Unit", unit, "price") or 0
	scored = _score(
		source=source or "walk-in",
		stage="inquiry",
		kind=kind or "flat",
		budget=budget or 0,
		unit_price=unit_price,
	)
	doc = frappe.get_doc(
		{
			"doctype": "Lead",
			"lead_name": lead_name,
			"mobile_no": phone_key,
			"notes": note,
			"atlas_project": project,
			"atlas_unit": unit,
			"atlas_channel_company": channel_company,
			"atlas_stage": "inquiry",
			"atlas_source": source or "walk-in",
			"atlas_kind": kind or "Flat",
			"atlas_budget": budget,
			"atlas_score": scored["score"],
			"atlas_band": scored["band"],
			"atlas_score_model": scored["model"],
			"status": "Open",
		}
	)
	doc.insert(ignore_permissions=True)
	return {
		"lead": doc.name,
		"stage": "inquiry",
		"band": scored["band"],
		"score": scored["score"],
		"served_by": scored["served_by"],
	}


@frappe.whitelist()
def advance_lead(lead: str):
	doc = frappe.get_doc("Lead", lead)
	stage = doc.get("atlas_stage") or "inquiry"
	err = refuse_advance(stage=stage)
	if err:
		frappe.throw(_(err))
	nxt = next_stage(stage)
	if not nxt:
		frappe.throw(_("Cannot advance from {0}.").format(stage))
	doc.atlas_stage = nxt
	if nxt == "won":
		doc.status = "Converted"
	doc.save()
	return {"lead": doc.name, "stage": nxt}


def _score(*, source, stage, kind, budget, unit_price) -> dict:
	payload = catboost_payload(
		source=source, stage=stage, kind=(kind or "flat").lower(), budget=budget, unit_price=unit_price
	)
	url = frappe.conf.get("atlas_scoring_url")
	if url:
		try:
			req = urllib.request.Request(
				url,
				data=json.dumps(payload).encode("utf-8"),
				headers={"Content-Type": "application/json"},
				method="POST",
			)
			with urllib.request.urlopen(req, timeout=3) as resp:
				body = json.loads(resp.read().decode("utf-8"))
			return apply_external_score(payload, body)
		except Exception:
			pass
	return hybrid_score(source=source, stage=stage, budget=budget, unit_price=unit_price)


@frappe.whitelist()
def customer_360(phone: str):
	from erpatlas.pipeline.customer import customer_file

	key = normalize_phone(phone)
	leads = []
	bookings = []
	commissions = []
	if key:
		leads = frappe.get_all(
			"Lead",
			filters={"mobile_no": ["like", f"%{key}%"]},
			fields=["name", "lead_name", "atlas_stage", "atlas_project", "atlas_unit", "mobile_no"],
		)
		if frappe.db.exists("DocType", "Atlas Booking"):
			units = [row.atlas_unit for row in leads if row.get("atlas_unit")]
			if units:
				bookings = frappe.get_all(
					"Atlas Booking",
					filters={"unit": ["in", units]},
					fields=["name", "status", "unit", "project", "collected", "total_consideration"],
				)
		if frappe.db.exists("DocType", "Atlas Commission"):
			parents = [b.name for b in bookings]
			if parents:
				commissions = frappe.get_all(
					"Atlas Commission",
					filters={"booking": ["in", parents]},
					fields=["name", "amount", "status", "booking"],
				)
	return customer_file(phone=key, leads=leads, bookings=bookings, commissions=commissions)
