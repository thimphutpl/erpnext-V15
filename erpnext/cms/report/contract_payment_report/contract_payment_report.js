// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Contract Payment Report"] = {
	"filters": [
		{	
			"fieldname": "contract",
			"label": ("Contract"),
			"fieldtype": "Link",
			"options": "Contract Details",
			"reqd":0,
			"width": "100"
		},
		{
			"fieldname":"reference_number",
			"label": ("Reference Number"),
			"fieldtype": "Data",
			"width": "80",
		},
		{
			"fieldname":"focal_person",
			"label": ("Focal Person"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": "120",
		},

		{	
			"fieldname": "supplier",
			"label": ("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"width": "100",
			
		}

	]
};
