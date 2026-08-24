from frappe import _


def get_data():
	return [
		{
			"module_name": "Property Inventory",
			"type": "module",
			"label": _("Flats and shops"),
		},
		{
			"module_name": "Approvals",
			"type": "module",
			"label": _("Waiting for a yes"),
		},
		{
			"module_name": "Booking",
			"type": "module",
			"label": _("Bookings"),
		},
	]
