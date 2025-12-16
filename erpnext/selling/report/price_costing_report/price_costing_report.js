// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Price Costing Report"] = {
	"filters": [
		{
			"fieldname":"price_costing_name",
			"label": ("Price Costing Name"),
			"fieldtype": "Data",
			"width": "100",
		},
		{
			"fieldname":"purchase_type",
			"label": ("Purchase Type"),
			"fieldtype": "Data",
			"width": "100",
		},
		{
			"fieldname":"item",
			"label": ("Item"),
			"fieldtype": "Link",
			"options": "Item",
			"width": "100",
		},
	]
};
