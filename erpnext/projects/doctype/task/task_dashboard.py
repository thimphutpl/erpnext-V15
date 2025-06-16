from frappe import _


def get_data():
	return {
		"fieldname": "task",
		"internal_links": {
			"Stock Entry": ["items", "task"],
			"Material Request": ["items", "task"],
		},
		"transactions": [
			{	"label": _("Material"), 
				"items": ["Material Request", "Stock Entry"]
			},
		],
	}
	pass
