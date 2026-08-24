app_name = "erpatlas"
app_title = "ERPATLAS"
app_publisher = "Atlas"
app_description = "Real-estate ERP on ERPNext"
app_email = "md@atlas.local"
app_license = "mit"

required_apps = ["erpnext"]

after_install = "erpatlas.setup.install.after_install"

fixtures = [
	{"dt": "Role", "filters": [["name", "in", [
		"Atlas Developer Admin",
		"Atlas Project Director",
		"Atlas Sales Manager",
		"Atlas Channel Admin",
		"Atlas Channel Agent",
		"Atlas Commercial",
		"Atlas Finance",
		"Atlas Site",
		"Atlas Stores",
		"Atlas Land Legal",
		"Atlas Documents",
	]]]},
]

atlas_has_today_report = ["erpatlas.channel.adapter.has_today_report"]

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
extend_doctype_class = {
	"Sales Order": "erpatlas.books.sales_order.AtlasSalesOrderMixin",
	"Supplier": "erpatlas.commercial.supplier.AtlasSupplierMixin",
	"Lead": "erpatlas.pipeline.lead.AtlasLeadMixin",
}


scheduler_events = {
	"daily": [
		"erpatlas.property_inventory.lock_adapter.expire_due_holds",
		"erpatlas.command.snapshot.capture_snapshot",
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
	"Atlas Booking": "erpatlas.booking.permissions.booking_query",
	"Atlas Commission": "erpatlas.booking.permissions.commission_query",
	"Atlas Handover Case": "erpatlas.handover.permissions.handover_query",
	"Atlas Snag": "erpatlas.handover.permissions.snag_query",
	"Atlas Daily Report": "erpatlas.channel.permissions.daily_report_query",
	"Lead": "erpatlas.pipeline.permissions.lead_query",
}

has_permission = {
	"Atlas Unit": "erpatlas.property_inventory.permissions.has_unit_permission",
	"Atlas Unit Hold": "erpatlas.property_inventory.permissions.has_hold_permission",
	"Atlas Channel Company": "erpatlas.property_inventory.permissions.has_channel_company_permission",
	"Atlas Booking": "erpatlas.booking.permissions.has_booking_permission",
	"Atlas Commission": "erpatlas.booking.permissions.has_commission_permission",
	"Atlas Handover Case": "erpatlas.handover.permissions.has_handover_permission",
	"Atlas Snag": "erpatlas.handover.permissions.has_snag_permission",
	"Atlas Daily Report": "erpatlas.channel.permissions.has_daily_report_permission",
	"Lead": "erpatlas.pipeline.permissions.has_lead_permission",
}
