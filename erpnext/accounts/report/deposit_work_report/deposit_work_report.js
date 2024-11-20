// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Deposit Work Report"] = {
	"filters": [
		{
			"fieldname" : "branch",
			"label" : ("Branch"),
			"fieldtype" : "Link",
			"options": "Branch",
			"width" : "120",
		},
		{
			"fieldname" : "from_date",
			"label" : ("From Date"),
			"fieldtype" : " Date",
			"width" : "100",
		},
		{
			"fieldname": "to_date",
			"label" : ("To Date"),
			"fieldtype" : "Date",
			"width" : "100"
		},
	]
}
