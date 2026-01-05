// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Status Report"] = {
	"filters": [
		{
			"fieldname":"customer",
			"label": ("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": "100",
		},
		{
			"fieldname":"item_code",
			"label": ("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": "100",
		},
	]
};
