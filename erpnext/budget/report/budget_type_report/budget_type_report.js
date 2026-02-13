// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Budget Type Report"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1 
		},
		{
			"fieldname":"cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center"
		},
		{
			"fieldname":"budget_type",
			"label": __("Budget Type"),
			"fieldtype": "Link",
			"options": "Budget Type",
			"reqd": 1 
		},
		{
			"fieldname":"aggregate",
			"label": __("Aggregate"),
			"fieldtype": "Check",
			"Default": 1
		},
		{
			"fieldname":"fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"reqd": 1 
		},
		
	]
};
