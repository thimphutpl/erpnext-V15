// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Budget Proposal Report"] = {

    // onload: function (report) {
    //     frappe.db.get_value(
    //         "Company",
    //         report.get_filter_value("company"),
    //         "program_code"
    //     ).then(r => {
    //         report.program_code = r.message.program_code;
    //         report.refresh();
    //     });
    // },
    "filters": [
        {
            "fieldname": "fiscal_year",
            "label": __("Fiscal Year"),
            "fieldtype": "Link",
            "options": "Fiscal Year",
            "default": frappe.defaults.get_user_default("fiscal_year"),
            "reqd": 1,
            "on_change": function (query_report) {
                var fiscal_year = query_report.get_values().fiscal_year;
                if (!fiscal_year) {
                    return;
                }
                frappe.call({
                    method: "frappe.client.get_value",
                    args: {
                        "doctype": "Fiscal Year",
                        "filters": { "name": fiscal_year },
                        "fieldname": ["year_start_date", "year_end_date"]
                    },
                    callback: function (r) {
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
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "on_change": function (query_report) {
                set_program_code(query_report);
            }
        },
        {
            "fieldname": "budget_activity",
            "label": __("Budget Activity"),
            "fieldtype": "Link",
            "options": "Budget Activity",
        },
        {
            "fieldname": "budget_sub_activity",
            "label": __("Budget Sub Activity"),
            "fieldtype": "Link",
            "options": "Budget Sub Activity",
        },
        {
            "fieldname": "source_of_fund",
            "label": __("Source of Fund"),
            "fieldtype": "Link",
            "options": "Source Of Fund",
        },
        {
            "fieldname": "budget_against",
            "label": __("Budget Against"),
            "fieldtype": "Select",
            "options": ["", __("Cost Center")],
            on_change: function (query_report) {
                var budget_against = frappe.query_report.get_filter_value('budget_against');
                var cost_center_filter = frappe.query_report.get_filter("cost_center");
                var project_filter = frappe.query_report.get_filter("project");
                var group_by_account_filter = frappe.query_report.get_filter("group_by_account");
                var controllable_filter = frappe.query_report.get_filter("controllable");
                var budget_type_filter = frappe.query_report.get_filter("budget_type");

                if (budget_against == "Project") {
                    if (cost_center_filter) cost_center_filter.toggle(false);
                    if (project_filter) project_filter.toggle(true);
                    if (group_by_account_filter) group_by_account_filter.toggle(false);
                    if (controllable_filter) controllable_filter.toggle(false);
                    if (budget_type_filter) budget_type_filter.toggle(false);
                } else {
                    if (cost_center_filter) cost_center_filter.toggle(true);
                    if (project_filter) project_filter.toggle(false);
                    if (group_by_account_filter) group_by_account_filter.toggle(true);
                    if (controllable_filter) controllable_filter.toggle(true);
                    if (budget_type_filter) budget_type_filter.toggle(true);
                }
                query_report.trigger_refresh();
            },
            "reqd": 1,
            "default": "Cost Center"
        },
        {
            "fieldname": "cost_center",
            "label": __("Branch"),
            "fieldtype": "Link",
            "options": "Cost Center",
            "get_query": function () {
                return {
                    'filters': [
                        ['Cost Center', 'disabled', '!=', '1']
                    ]
                };
            }
        },
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "hidden": 1
        },
        {
            "fieldname": "group_by_account",
            "label": __("Group By Account"),
            "fieldtype": "Check",
            "default": 0,
        },
        {
            "fieldname": "controllable",
            "label": __("Controllable"),
            "fieldtype": "Check",
            "default": 0,
        },
        {
            "fieldname": "budget_type",
            "label": __("Budget Type"),
            "fieldtype": "Link",
            "options": "Budget Type",
            "ignore_user_permissions": 1
        },
        {
            "fieldname": "month",
            "label": __("Month"),
            "fieldtype": "Select",
            "width": "100",
            "options": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        },
    ],

    "onload": function (query_report) {
        // Initially hide month filter (as per original requirement)
        var month_filter = query_report.get_filter("month");
        if (month_filter) {
            month_filter.toggle(false);
        }

        // Set initial visibility for other filters based on default budget_against
        var budget_against = query_report.get_values().budget_against;
        var cost_center_filter = query_report.get_filter("cost_center");
        var project_filter = query_report.get_filter("project");
        var group_by_account_filter = query_report.get_filter("group_by_account");
        var controllable_filter = query_report.get_filter("controllable");
        var budget_type_filter = query_report.get_filter("budget_type");

        if (budget_against == "Project") {
            if (cost_center_filter) cost_center_filter.toggle(false);
            if (project_filter) project_filter.toggle(true);
            if (group_by_account_filter) group_by_account_filter.toggle(false);
            if (controllable_filter) controllable_filter.toggle(false);
            if (budget_type_filter) budget_type_filter.toggle(false);
        } else {
            if (cost_center_filter) cost_center_filter.toggle(true);
            if (project_filter) project_filter.toggle(false);
            if (group_by_account_filter) group_by_account_filter.toggle(true);
            if (controllable_filter) controllable_filter.toggle(true);
            if (budget_type_filter) budget_type_filter.toggle(true);
        }

        // Auto-set from_date and to_date when fiscal_year is selected (if not already set)
        var fiscal_year = query_report.get_values().fiscal_year;
        if (fiscal_year && (!query_report.get_values().from_date || !query_report.get_values().to_date)) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    "doctype": "Fiscal Year",
                    "filters": { "name": fiscal_year },
                    "fieldname": ["year_start_date", "year_end_date"]
                },
                callback: function (r) {
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

function set_program_code(report) {

    let company = report.get_filter_value("company");

    if (!company) {
        report.program_code = "";
        report.program_name = "";
        report.refresh();
        return;
    }

    frappe.db.get_value(
        "Company",
        company,
        [
            "program_code",
            "program_name"
        ]
    ).then(r => {

        report.program_code = r.message.program_code || "";
        report.program_name = r.message.program_name || "";

        report.refresh();

    });
}
