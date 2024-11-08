from frappe import _


def get_data():
	return {
        "fieldname": "reference_name",
		# "non_standard_fieldnames": {"Abstract Bill": "reference_name"},
		"transactions": [
			{"label": _("Related Transaction"), "items": ["Journal Entry"]},
		],
	}
