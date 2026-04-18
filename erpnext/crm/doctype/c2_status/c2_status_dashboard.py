from frappe import _

def get_data():
	return {
		"fieldname": "c2_status",
		"non_standard_fieldnames": {"Purchase Order Item": "c2_status"},
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
