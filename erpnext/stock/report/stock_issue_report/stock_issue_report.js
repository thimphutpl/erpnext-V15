// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// frappe.query_reports["Stock Issue Report"] = {
// 	"filters": [

// 	]
// };

frappe.query_reports["Stock Issue Report"] = {
	"filters": [
		{
			"fieldname": "purpose",
			"label": __("Purpose"),
			"fieldtype": "Select",
			"width": "80",
			"options": ["Material Issue", "Material Transfer"],
			"reqd": 1
		},

		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.boot.sysdefaults.year_start_date || frappe.datetime.get_today(),
		},

		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.get_today()
		},

		{
			"fieldname": "warehouse",
			"label": __("From Warehouse"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Warehouse"
		},

		{
			"fieldname": "cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Cost Center"
		},

		{
			"fieldname": "item_code",
			"label": __("Material Code"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item"
		}
	]
}

