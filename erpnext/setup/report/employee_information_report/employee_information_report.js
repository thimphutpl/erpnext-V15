// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Information Report"] = {
	"filters": [
		
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nAll\nActive\nIn Active\nLeft",
			"default": "All"
		},
		{
			"fieldname": "date_of_joining",
			"label": __("Date of Joining"),
			"fieldtype": "Date Range",
			"reqd": 0,  
		},
		{
			"fieldname": "branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options":"Branch",
			"reqd": 0,  
		},
		

	]
};
