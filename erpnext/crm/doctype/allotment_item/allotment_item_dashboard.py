from frappe import _

def get_data():
	return {
		"fieldname": "allotment_item",
		"transactions": [
			{
				"label": _("Reference"),
				"items": ["Purchase Order", "C2 Status", "Sales Order"]
			},
		],
	}
