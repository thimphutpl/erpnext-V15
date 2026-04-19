// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Job Cards Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"width": 100
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"width": 100
		},
		{
			"fieldname": "branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"width": 150
		},
		{
			"fieldname": "customer",
			"label": __("Customer Name"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150
		},
		{
			"fieldname": "job_card_no",
			"label": __("Job Card Number"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "registration_no",
			"label": __("Registration No"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "repair_type",
			"label": __("Repair Type"),
			"fieldtype": "Select",
			"options": ["", "Pre-Delivery Inspection", "Periodic Maintenance", "General Repair", "Body and Paint", "Others"],
			"width": 200
		}
	]
};