// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Project Progress Report"] = {
	"filters": [
		{
			"fieldname": "cost_center",
			"label": ("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"on_change": function(query_report) {
				frappe.query_report.set_filter_value("project_definition", null);
				frappe.query_report.set_filter_value("project", null);
				frappe.query_report.set_filter_value("task", null);
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "project_definition",
			"label": ("Gyalsung Academy(Project Definition)"),
			"fieldtype": "Link",
			"options": "Project Definition",
			"get_query": function() {
				var cost_center = frappe.query_report.get_filter_value("cost_center")
				return {
					'doctype': "Project Definition",
					'filters': [['cost_center', '=', cost_center]]
				}
			},
			"on_change": function(query_report) {
				frappe.query_report.set_filter_value("project", null);
				frappe.query_report.set_filter_value("task", null);
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "project",
			"label": ("Activity(Project)"),
			"fieldtype": "Link",
			"options": "Project",
			"get_query": function() {
				var project_definition = frappe.query_report.get_filter_value("project_definition")
				return { 'doctype': "Project",
						'filters': [
								['project_definition', '=', project_definition]
				]}
			},
			"on_change": function(query_report) {
				frappe.query_report.set_filter_value("task", null);
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "task",
			"label": ("Task"),
			"fieldtype": "Link",
			"options": "Task",
			"get_query": function() {
				var project = frappe.query_report.get_filter_value("project")
				return { 'doctype': "Task",
						'filters': [
								['project', '=', project]
				]}
			},
		},
	]
};
