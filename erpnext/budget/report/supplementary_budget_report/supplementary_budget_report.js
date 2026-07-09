// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Supplementary Budget Report"] = {
	"filters": [
		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": frappe.defaults.get_user_default("fiscal_year"),
			"reqd": 1,
			"on_change": function(query_report) {
				var fiscal_year = query_report.get_values().fiscal_year;
				if (!fiscal_year) {
					return;
				}
				frappe.call({
					method: "frappe.client.get_value",
					args: {
						"doctype": "Fiscal Year",
						"filters": {"name": fiscal_year},
						"fieldname": ["year_start_date", "year_end_date"]
					},
					callback: function(r) {
						if (r.message) {
							// Set the from_date and to_date filters
							var from_date_filter = query_report.get_filter("from_date");
							var to_date_filter = query_report.get_filter("to_date");
							
							if (from_date_filter) {
								from_date_filter.set_value(r.message.year_start_date);
							}
							if (to_date_filter) {
								to_date_filter.set_value(r.message.year_end_date);
							}
							
							// Refresh the report
							query_report.trigger_refresh();
						}
					}
				});
			}
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_start_date"),
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_end_date"),
		},
		{
			"fieldname":"budget_against",
			"label": __("Budget Against"),
			"fieldtype": "Select",
			"options": ["", __("Cost Center"), __("Project")],
			on_change: function(query_report){
				var budget_against = query_report.get_filter_value('budget_against');
				var to_acc_filter = query_report.get_filter("to_acc");
				var to_project_filter = query_report.get_filter("to_project");
				var to_cc_filter = query_report.get_filter("to_cc");
				
				if(budget_against == "Project"){
					if (to_acc_filter) to_acc_filter.toggle(false);
					if (to_project_filter) to_project_filter.toggle(true);
					if (to_cc_filter) to_cc_filter.toggle(false);
				} else if(budget_against == "Cost Center"){
					if (to_acc_filter) to_acc_filter.toggle(true);
					if (to_project_filter) to_project_filter.toggle(false);
					if (to_cc_filter) to_cc_filter.toggle(true);
				} else {
					// Default case when no option selected
					if (to_acc_filter) to_acc_filter.toggle(true);
					if (to_project_filter) to_project_filter.toggle(false);
					if (to_cc_filter) to_cc_filter.toggle(true);
				}
				query_report.trigger_refresh();
			},
			"reqd": 1,
			"default": "Cost Center"
		},
		{
			"fieldname": "to_project",
			"label": __("To Project"),
			"fieldtype": "Link",
			"options": "Project",
			"hidden": 1  // Hidden by default since default is Cost Center
		},
		{
			"fieldname": "to_cc",
			"label": __("To Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"get_query": function() {
				return {
					'filters': [
						['Cost Center', 'disabled', '!=', '1']
					]
				};
			}
		},
		{
			"fieldname": "to_acc",
			"label": __("To Account"),
			"fieldtype": "Link",
			"options": "Account",
			"get_query": function() {
				return {
					'filters': [
						['Account', 'disabled', '!=', '1']
					]
				};
			}
		},
	],
	
	"onload": function(query_report) {
		// Set initial visibility for filters based on default budget_against
		var budget_against = query_report.get_values().budget_against;
		var to_acc_filter = query_report.get_filter("to_acc");
		var to_project_filter = query_report.get_filter("to_project");
		var to_cc_filter = query_report.get_filter("to_cc");
		
		if (budget_against == "Project") {
			if (to_acc_filter) to_acc_filter.toggle(false);
			if (to_project_filter) to_project_filter.toggle(true);
			if (to_cc_filter) to_cc_filter.toggle(false);
		} else if (budget_against == "Cost Center") {
			if (to_acc_filter) to_acc_filter.toggle(true);
			if (to_project_filter) to_project_filter.toggle(false);
			if (to_cc_filter) to_cc_filter.toggle(true);
		} else {
			// Default to Cost Center behavior
			if (to_acc_filter) to_acc_filter.toggle(true);
			if (to_project_filter) to_project_filter.toggle(false);
			if (to_cc_filter) to_cc_filter.toggle(true);
		}
		
		// Auto-set from_date and to_date when fiscal_year is selected (if not already set)
		var fiscal_year = query_report.get_values().fiscal_year;
		if (fiscal_year && (!query_report.get_values().from_date || !query_report.get_values().to_date)) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					"doctype": "Fiscal Year",
					"filters": {"name": fiscal_year},
					"fieldname": ["year_start_date", "year_end_date"]
				},
				callback: function(r) {
					if (r.message) {
						var from_date_filter = query_report.get_filter("from_date");
						var to_date_filter = query_report.get_filter("to_date");
						
						if (from_date_filter && !query_report.get_values().from_date) {
							from_date_filter.set_value(r.message.year_start_date);
						}
						if (to_date_filter && !query_report.get_values().to_date) {
							to_date_filter.set_value(r.message.year_end_date);
						}
					}
				}
			});
		}
	}
}