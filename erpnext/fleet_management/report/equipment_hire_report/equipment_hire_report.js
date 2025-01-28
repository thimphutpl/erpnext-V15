// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Equipment Hire Report"] = {
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
			default: frappe.datetime.month_start(),
		},
		{
			"fieldname":"to_date",
			"label": ("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "customer",
			"label": ("Customer"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Customer"
		},
		{
			"fieldname": "not_cdcl",
			"label": ("Include Only Gyalsung Equipments"),
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname": "include_disabled",
			"label": ("Include Disbaled Equipments"),
			"fieldtype": "Check",
			"default": 0
		},
	]
};
