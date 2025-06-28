// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Compact Report"] = {
	"filters": [
		{
			"fieldname":"fiscal_year",
			"label": ("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"width": "100",
			"reqd": 1
		},
		{
			"fieldname":"company",
			"label": ("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"width": "100",
			"reqd": 1
		},
	]
};
