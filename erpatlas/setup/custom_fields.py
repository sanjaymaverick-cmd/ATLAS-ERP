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
	],
}


def ensure_custom_fields():
	import frappe
	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True, update=True)
	frappe.clear_cache()
