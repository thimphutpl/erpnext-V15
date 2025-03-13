// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Check Asset Depreciation"] = {
	"filters": [
		{
			"fieldname": "fiscal_year",
			"label": ("Fiscal Year"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Fiscal Year",

		},
		{
			"fieldname":"month",
			"label": ("Month"),
			"fieldtype": "Select",
			"width": "80",
			"options":"\nJan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSept\nOct\nNov\nDec",
			"reqd": 1
		},
	]
};
