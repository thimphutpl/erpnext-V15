// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Scholarship Report"] = {
	"filters":
		[
			{
				"fieldname": "college",
				"label": "College",
				"fieldtype": "Data",
				"options": "College"
			},
			{
				"fieldname": "cid_number",
				"label": "CID Number",
				"fieldtype": "Data"
			},
			{
				"fieldname": "name1",
				"label": "Student Name",
				"fieldtype": "Data"
			},
			{
				"fieldname": "country",
				"label": "Country",
				"fieldtype": "Link",
				"options": "Country"
			},
			{
				"fieldname": "status",
				"label": "Status",
				"fieldtype": "Data",
				"options": "Status"
			}
		]
};
