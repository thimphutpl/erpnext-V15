from frappe import _


def get_data():
	return {
		"fieldname": "journal_entry",
		"non_standard_fieldnames": {
			"Journal Entry": "reference_name",
		},
	
		"transactions": [
			{"label": _("Payment"), "items": [ "Journal Entry"]},
		],
	}
