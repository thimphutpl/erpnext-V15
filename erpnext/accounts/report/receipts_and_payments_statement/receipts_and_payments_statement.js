// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Receipts and Payments Statement"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		// {
		// 	fieldname: "cost_center",
		// 	label: __("Cost Center"),
		// 	fieldtype: "Link",
		// 	options: "Cost Center",
		// 	default: frappe.defaults.get_user_default("Cost Center"),
		// },
		{
			"fieldname": "cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"get_query": function() {return {'filters': [['Cost Center', 'disabled', '!=', '1']]}}
		},
		{
			"fieldname": "business_activity",
			"label": __("Business Activity"),
			"fieldtype": "Link",
			"options": "Business Activity",
		},
	]
};
