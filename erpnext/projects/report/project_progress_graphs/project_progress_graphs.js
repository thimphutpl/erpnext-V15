// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Project Progress Graphs"] = {

	"filters": [
		{
			"fieldname": "project_defination",
			"label": ("Project Definition"),
			"fieldtype": "Link",
			"options": "Project Definition",
			// "get_query": function() {
			// 	return {
			// 		'doctype': "Project",
			// 		'filters': [
			// 			['is_group', '=', '1']
			// 		]
			// 	}
			// },
		},
		{
			"fieldname": "project",
			"label": ("Project"),
			"fieldtype": "Link",
			"options": "Project",
			// "get_query": function() {
			// 	var parent_project = frappe.query_report.filters_by_name.project.get_value();
			// 	return { 'doctype': "Project",
			// 		'filters': [
			// 			['project_defination', '=', parent_project]
			// 		]		
			// 	};			
			// }
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1
		},
		{
			fieldname: "range",
			label: __("Range"),
			fieldtype: "Select",
			options: [{ "value": "Monthly", "label": __("Monthly") }],
			default: "Monthly",
			reqd: 0
		}
	],

	onload: function(report) {
		report.page.set_title("Project Progress Graphs");
	},	
};
