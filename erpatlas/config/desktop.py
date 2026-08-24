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
		{
			"module_name": "Handover",
			"type": "module",
			"label": _("Keys and snags"),
		},
		{
			"module_name": "Channel",
			"type": "module",
			"label": _("Channel companies"),
		},
		{
			"module_name": "Command",
			"type": "module",
			"label": _("Command"),
		},
	]
