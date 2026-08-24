"""One-shot Desk UAT on a live site. bench --site SITE execute erpatlas.setup.uat.run"""

from __future__ import annotations


def run():
	import frappe

	frappe.set_user("Administrator")
	apps = frappe.get_installed_apps()
	print("APPS", apps)
	if "erpatlas" not in apps:
		raise RuntimeError("erpatlas is not installed")

	from erpatlas.analytics.board import get_sales_analytics
	from erpatlas.command.board import get_command

	cmd = get_command()
	print(
		"COMMAND",
		"cash=",
		cmd.get("shows_cash"),
		"money=",
		cmd.get("shows_money"),
		"pending=",
		cmd["approvals"]["pending"],
	)
	funnel = get_sales_analytics()
	print("FUNNEL", [(r["stage"], r["count"]) for r in funnel["funnel"]])

	company = "MOCK ATLAS3 LLP"
	existing = frappe.db.get_value("Project", {"project_name": "UAT Lake"})
	if existing:
		proj_name = existing
	else:
		proj_name = frappe.get_doc(
			{"doctype": "Project", "project_name": "UAT Lake", "company": company}
		).insert(ignore_permissions=True).name
	print("PROJECT", proj_name)

	parcel = frappe.get_doc(
		{
			"doctype": "Atlas Parcel",
			"project": proj_name,
			"title": "Muhana Mandi khasra 41/2",
			"khasra": "41/2",
			"area": "3600 sq yd",
		}
	).insert(ignore_permissions=True)
	print("PARCEL", parcel.name, parcel.status)

	from erpatlas.land.adapter import acquire_parcel, start_title_pack

	pack = start_title_pack(parcel.name)
	print("PACK", pack["status"], "added", len(pack["added"]))
	if pack["status"] != "diligence" or len(pack["added"]) != 5:
		raise RuntimeError("title pack did not open")

	blocked = False
	try:
		acquire_parcel(parcel.name, consideration=1, sale_deed_no="SD-1")
	except frappe.ValidationError as e:
		blocked = "must be clear" in str(e)
		print("ACQUIRE_BLOCKED", str(e)[:180])
	if not blocked:
		raise RuntimeError("acquire should refuse open diligence")

	if not frappe.db.exists("Atlas Channel Company", "UAT Pink City"):
		frappe.get_doc(
			{
				"doctype": "Atlas Channel Company",
				"company_name": "UAT Pink City",
				"city": "Jaipur",
				"status": "Active",
			}
		).insert(ignore_permissions=True)
	print("CHANNEL UAT Pink City")
	print("UAT_OK")
