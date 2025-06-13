// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Asset Report"] = {
	"filters": [
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"on_change": function(query_report) {
				var emp = query_report.get_values().employee;
				if (!emp) {
					query_report.set_filter_value("employee_name", "");
				}
		
				frappe.model.with_doc("Employee", emp, function(r) {
					var fy = frappe.model.get_doc("Employee", emp);
					query_report.set_filter_value("employee_name", fy.employee_name);
				});
			}
		},
		{
			"fieldname": "employee_name",
			"label": __("Employee Name"),
			"fieldtype": "Data",
			"read_only": 1
		},
	]
};
