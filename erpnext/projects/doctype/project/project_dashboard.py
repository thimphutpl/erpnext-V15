from frappe import _


def get_data():
	return {
		"heatmap": True,
		"heatmap_message": _("This is based on the Time Sheets created against this project"),
		"fieldname": "project",
		
		"internal_links": {
			"Stock Entry": ["items", "project"]
		},
		"transactions": [
			{
				"label": _("Project"),
				"items": ["Task"],
			},
			{	"label": _("Material"), 
				"items": ["Material Request", "BOQ", "BOQ Adjustment","Stock Entry"]
			},
			{
				"label": _("Purchase"), 
				"items": ["Purchase Order", "Purchase Receipt", "Purchase Invoice"]
			},
			{
				"label": _("Transactions"), 
				"items": ["Project Advance", "Project Invoice", "Project Payment", "MB Entry", "Journal Entry"]
			},
		],
	}
