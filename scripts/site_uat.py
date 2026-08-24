"""Server-side Desk UAT on site frontend. Run from frappe-bench with env python."""
from __future__ import annotations

import os
import sys

os.chdir("/home/frappe/frappe-bench")
sys.path.insert(0, os.getcwd())

import frappe

frappe.init(site="frontend", sites_path="sites")
frappe.connect()
frappe.set_user("Administrator")
frappe.flags.ignore_csrf = True

out = []


def log(msg):
	out.append(msg)
	print(msg)


try:
	apps = frappe.get_installed_apps()
	log(f"APPS {apps}")
	assert "erpatlas" in apps

	from erpatlas.command.board import get_command
	from erpatlas.analytics.board import get_sales_analytics

	cmd = get_command()
	log(f"COMMAND cash={cmd.get('shows_cash')} money={cmd.get('shows_money')} pending={cmd['approvals']['pending']}")
	funnel = get_sales_analytics()
	log(f"FUNNEL {[ (r['stage'], r['count']) for r in funnel['funnel'] ]}")

	company = "MOCK ATLAS3 LLP"
	if not frappe.db.exists("Project", {"project_name": "UAT Lake"}):
		proj = frappe.get_doc(
			{"doctype": "Project", "project_name": "UAT Lake", "company": company}
		).insert(ignore_permissions=True)
	else:
		proj = frappe.get_doc("Project", {"project_name": "UAT Lake"})
	log(f"PROJECT {proj.name}")

	parcel = frappe.get_doc(
		{
			"doctype": "Atlas Parcel",
			"project": proj.name,
			"title": "Muhana Mandi khasra 41/2",
			"khasra": "41/2",
			"area": "3600 sq yd",
		}
	).insert(ignore_permissions=True)
	log(f"PARCEL {parcel.name} {parcel.status}")

	from erpatlas.land.adapter import start_title_pack

	pack = start_title_pack(parcel.name)
	log(f"PACK added={len(pack['added'])} status={pack['status']}")
	assert pack["status"] == "diligence"
	assert len(pack["added"]) == 5

	from erpatlas.land.adapter import acquire_parcel

	try:
		acquire_parcel(parcel.name, consideration=1, sale_deed_no="SD-1")
		raise SystemExit("acquire should refuse open diligence")
	except frappe.ValidationError as e:
		log(f"ACQUIRE_BLOCKED {e}")

	if not frappe.db.exists("Atlas Channel Company", "UAT Pink City"):
		cc = frappe.get_doc(
			{
				"doctype": "Atlas Channel Company",
				"company_name": "UAT Pink City",
				"city": "Jaipur",
				"status": "Active",
			}
		).insert(ignore_permissions=True)
		log(f"CHANNEL {cc.name}")
	else:
		log("CHANNEL UAT Pink City")

	log("UAT_OK")
	frappe.db.commit()
finally:
	frappe.destroy()
