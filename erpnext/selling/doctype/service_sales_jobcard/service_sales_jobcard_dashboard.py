from frappe import _

def get_data():
	return {
		"fieldname": "service_sales_jobcard",
		"non_standard_fieldnames": {
			"Sales Order": "service_sales_jobcard",
		},
		"transactions": [
			{
				"label": _("Selling"),
				"items": ["Sales Order"]
			},
		],
	}
