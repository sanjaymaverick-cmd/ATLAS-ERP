app_name = "erpatlas"
app_title = "ERPATLAS"
app_publisher = "Atlas"
app_description = "Real-estate ERP on ERPNext"
app_email = "md@atlas.local"
app_license = "mit"

required_apps = ["erpnext"]

after_install = "erpatlas.setup.install.after_install"

export_python_type_annotations = True

# Desk (Frappe v16)
add_to_apps_screen = [
	{
		"name": "erpatlas",
		"logo": "/assets/erpatlas/logo.png",
		"title": "ERPATLAS",
		"route": "/app/command",
	}
]

# Mixins on native DocTypes — v16+. Do not use override_doctype_class.
extend_doctype_class = {}


scheduler_events = {
	"daily": [
		"erpatlas.property_inventory.lock_adapter.expire_due_holds",
	]
}

doc_events = {
	"Purchase Order": {
		"validate": "erpatlas.commercial.gates.validate_vendor_active",
	},
	"Payment Entry": {
		"validate": "erpatlas.approvals.guards.refuse_commission_auto_pay",
	},
}

permission_query_conditions = {
	"Atlas Unit": "erpatlas.property_inventory.permissions.unit_query",
	"Atlas Unit Hold": "erpatlas.property_inventory.permissions.hold_query",
	"Atlas Channel Company": "erpatlas.property_inventory.permissions.channel_company_query",
	"Atlas Approval": "erpatlas.approvals.permissions.approval_query",
}

has_permission = {
	"Atlas Unit": "erpatlas.property_inventory.permissions.has_unit_permission",
	"Atlas Unit Hold": "erpatlas.property_inventory.permissions.has_hold_permission",
	"Atlas Channel Company": "erpatlas.property_inventory.permissions.has_channel_company_permission",
}
