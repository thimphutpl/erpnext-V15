// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Common Pool Vehicle Queue"] = {
	"filters": [
		{
			"fieldname":"vehicle_capacity",
			"label": __("Vehicle Capacity"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Vehicle Capacity",
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			// "default": frappe.datetime.year_start(),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			// "default": frappe.datetime.get_today()
		},
	]
};
