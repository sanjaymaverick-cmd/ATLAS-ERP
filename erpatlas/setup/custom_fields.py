"""Custom fields on native ERPNext DocTypes. Created in after_install."""

from __future__ import annotations

CUSTOM_FIELDS = {
	"Sales Order": [
		{
			"fieldname": "atlas_booking",
			"label": "Atlas Booking",
			"fieldtype": "Link",
			"options": "Atlas Booking",
			"insert_after": "title",
			"read_only": 1,
		},
		{
			"fieldname": "atlas_unit",
			"label": "Atlas Unit",
			"fieldtype": "Link",
			"options": "Atlas Unit",
			"insert_after": "atlas_booking",
			"read_only": 1,
		},
	],
	"Sales Invoice": [
		{
			"fieldname": "atlas_booking",
			"label": "Atlas Booking",
			"fieldtype": "Link",
			"options": "Atlas Booking",
			"insert_after": "title",
			"read_only": 1,
		},
	],
	"Payment Entry": [
		{
			"fieldname": "atlas_booking",
			"label": "Atlas Booking",
			"fieldtype": "Link",
			"options": "Atlas Booking",
			"insert_after": "party",
			"read_only": 1,
		},
		{
			"fieldname": "atlas_approval",
			"label": "Atlas Approval",
			"fieldtype": "Link",
			"options": "Atlas Approval",
			"insert_after": "atlas_booking",
			"read_only": 1,
		},
	],
	"Lead": [
		{
			"fieldname": "atlas_project",
			"label": "Project",
			"fieldtype": "Link",
			"options": "Project",
			"insert_after": "lead_name",
			"in_standard_filter": 1,
		},
		{
			"fieldname": "atlas_unit",
			"label": "Unit",
			"fieldtype": "Link",
			"options": "Atlas Unit",
			"insert_after": "atlas_project",
		},
		{
			"fieldname": "atlas_channel_company",
			"label": "Channel Company",
			"fieldtype": "Link",
			"options": "Atlas Channel Company",
			"insert_after": "atlas_unit",
			"in_standard_filter": 1,
		},
		{
			"fieldname": "atlas_stage",
			"label": "Pipeline",
			"fieldtype": "Select",
			"options": "inquiry\ncontacted\nqualified\nvisit\nnegotiation\ndocumentation\nhandover\nwon\nlost\nnurture",
			"default": "inquiry",
			"insert_after": "atlas_channel_company",
			"in_standard_filter": 1,
		},
		{
			"fieldname": "atlas_source",
			"label": "Atlas source",
			"fieldtype": "Data",
			"insert_after": "atlas_stage",
		},
		{
			"fieldname": "atlas_kind",
			"label": "Kind",
			"fieldtype": "Select",
			"options": "Flat\nShop\nPlot",
			"insert_after": "atlas_source",
		},
		{
			"fieldname": "atlas_budget",
			"label": "Budget",
			"fieldtype": "Currency",
			"insert_after": "atlas_kind",
		},
		{
			"fieldname": "atlas_score",
			"label": "Score",
			"fieldtype": "Int",
			"read_only": 1,
			"insert_after": "atlas_budget",
		},
		{
			"fieldname": "atlas_band",
			"label": "Band",
			"fieldtype": "Select",
			"options": "hot\nwarm\ncool",
			"read_only": 1,
			"insert_after": "atlas_score",
		},
		{
			"fieldname": "atlas_score_model",
			"label": "Score model",
			"fieldtype": "Data",
			"read_only": 1,
			"insert_after": "atlas_band",
		},
		{
			"fieldname": "atlas_live_phone",
			"label": "Live phone",
			"fieldtype": "Data",
			"hidden": 1,
			"unique": 1,
			"read_only": 1,
			"no_copy": 1,
			"insert_after": "atlas_score_model",
		},
	],
	"Supplier": [
		{
			"fieldname": "atlas_stage",
			"label": "Atlas stage",
			"fieldtype": "Select",
			"options": "Draft\nApproval\nActive",
			"default": "Draft",
			"insert_after": "supplier_name",
		},
	],
	"Purchase Invoice": [
		{
			"fieldname": "atlas_commission",
			"label": "Atlas Commission",
			"fieldtype": "Link",
			"options": "Atlas Commission",
			"insert_after": "supplier",
			"read_only": 1,
		},
	],
	"Project": [
		{
			"fieldname": "gst_on_under_construction",
			"label": "GST on under-construction",
			"fieldtype": "Check",
			"default": "1",
			"insert_after": "company",
		},
		{
			"fieldname": "gst_rate",
			"label": "GST rate",
			"fieldtype": "Percent",
			"insert_after": "gst_on_under_construction",
		},
		{
			"fieldname": "atlas_tax_included",
			"label": "Tax included",
			"fieldtype": "Select",
			"options": "inclusive\nexclusive",
			"default": "inclusive",
			"insert_after": "gst_rate",
		},
		{
			"fieldname": "atlas_affordable",
			"label": "Affordable housing GST",
			"fieldtype": "Check",
			"insert_after": "atlas_tax_included",
		},
		{
			"fieldname": "atlas_sales_tax_template",
			"label": "Atlas sales tax template",
			"fieldtype": "Link",
			"options": "Sales Taxes and Charges Template",
			"insert_after": "atlas_affordable",
		},
		{
			"fieldname": "atlas_exclusive_channel_company",
			"label": "Exclusive Channel Company",
			"fieldtype": "Link",
			"options": "Atlas Channel Company",
			"insert_after": "atlas_sales_tax_template",
		},
	],
	"Purchase Order": [
		{
			"fieldname": "atlas_approval",
			"label": "Atlas Approval",
			"fieldtype": "Link",
			"options": "Atlas Approval",
			"insert_after": "supplier",
			"read_only": 1,
		},
		{
			"fieldname": "atlas_rfq",
			"label": "Atlas RFQ",
			"fieldtype": "Data",
			"insert_after": "atlas_approval",
			"read_only": 1,
		},
	],
}


def ensure_custom_fields():
	import frappe
	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True, update=True)
	frappe.clear_cache()
