// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Budget Proposal Report"] = {
	"onload": function(query_report) {
		var month_filter = query_report.get_filter("month");
		month_filter.toggle(false);
    },
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
				frappe.model.with_doc("Fiscal Year", fiscal_year, function(r) {
					var fy = frappe.model.get_doc("Fiscal Year", fiscal_year);
					query_report.filters_by_name.from_date.set_input(fy.year_start_date);
					query_report.filters_by_name.to_date.set_input(fy.year_end_date);
					query_report.trigger_refresh();
				});
			}
		},
		{
			"fieldname": "date",
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
				var budget_against = frappe.query_report.get_filter_value('budget_against');
				if(budget_against == "Project"){
					var cost_center = frappe.query_report.get_filter("cost_center"); cost_center.toggle(false);
					var project = frappe.query_report.get_filter("project"); project.toggle(true);
					var group_by_account = frappe.query_report.get_filter("group_by_account"); group_by_account.toggle(false);
					var controllable = frappe.query_report.get_filter("controllable"); controllable.toggle(false);	
					var budget_type = frappe.query_report.get_filter("budget_type"); budget_type.toggle(false);	
				}else{
					var cost_center = frappe.query_report.get_filter("cost_center"); cost_center.toggle(true);
					var project = frappe.query_report.get_filter("project"); project.toggle(false);	
					var group_by_account = frappe.query_report.get_filter("group_by_account"); group_by_account.toggle(true);
					var controllable = frappe.query_report.get_filter("controllable"); controllable.toggle(true);
					var budget_type = frappe.query_report.get_filter("budget_type"); budget_type.toggle(true);			
				}
				query_report.trigger_refresh();	
			},
			"reqd":1,
			"default":"Cost Center"
		},
		{
			"fieldname": "cost_center",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"get_query": function() {return {'filters': [['Cost Center', 'disabled', '!=', '1']]}}
		},
		{
			"fieldname": "budget_type",
			"label": __("Budget Type"),
			"fieldtype": "Link",
			"options": "Budget Type",
			"ignore_user_permissions":1
		},
		
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"width": "100",
			"options": ["January","February","March","April","May","June","July","August","September","October","November","December"],
		},
	
	],
   }
