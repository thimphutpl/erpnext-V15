// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Vehicle Logbook Report"] = {
	"filters": [
		{
			"fieldname": "branch",
			"label": ("Branch"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Branch",

		},
		{
			"fieldname":"from_date",
			"label": ("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd":1
		},
		{
			"fieldname":"to_date",
			"label": ("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd":1
		},
		{
			"fieldname":"project",
			"label": ("Project"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Project",
		},
		{
			"fieldname":"registration_number",
			"label": ("Registration Number"),
			"fieldtype": "Data",
			"width": "80",
		},
	]
};
