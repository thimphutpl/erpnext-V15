from frappe import _

def get_data():
	return {
		"fieldname": "c2_status",
		"non_standard_fieldnames": {
			"Sales Order": "c2_status",
			"Purchase Order": "c2_status",
		},
		"transactions": [
			{
				"label": _("Selling"),
				"items": ["Sales Order"]
			},
			{
				"label": _("Buying"),
				"items": ["Purchase Order"]
			},
		],
	}
