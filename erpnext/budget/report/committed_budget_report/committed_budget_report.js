// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Committed Budget Report"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        },
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
                    frappe.query_report.set_filter_value('from_date', fy.year_start_date);
                    frappe.query_report.set_filter_value('to_date', fy.year_end_date);
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
            "options": ["","Cost Center", "Project"],
            "default": "Cost Center",
            "on_change": function() {
                var budget_against = frappe.query_report.get_filter_value('budget_against');
                var cost_center = frappe.query_report.get_filter("cost_center");
                var project = frappe.query_report.get_filter("project");
                
                cost_center.df.hidden = budget_against !== "Cost Center";
                project.df.hidden = budget_against !== "Project";
                
                frappe.query_report.refresh();
            },
            "reqd": 1
        },
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "hidden": 1,
            "get_query": function() {
                return {
                    "filters": {
                        "status": "Open",
                    }
                }
            }
        },
        {
            "fieldname": "cost_center",
            "label": __("Cost Center"),
            "fieldtype": "Link",
            "options": "Cost Center",
            "get_query": function() {
                return {
                    "filters": {
                        "disabled": 0
                    }
                }
            }
        },
    ],
    "onload": function(report) {
        // Initialize hidden state of filters
        var budget_against = report.get_filter_value('' ||'budget_against') || "Cost Center" ;
        report.set_filter_value('budget_against', budget_against);
        
        var cost_center = report.get_filter("cost_center");
        var project = report.get_filter("project");
        
        cost_center.df.hidden = budget_against !== "Cost Center";
        project.df.hidden = budget_against !== "Project";
    }
};