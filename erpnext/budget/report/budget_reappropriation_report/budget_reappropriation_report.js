// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Budget Reappropriation Report"] = {
    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            "on_change": function (query_report) {
                set_program_code(query_report);
            }
        },
        {
            fieldname: "fiscal_year",
            label: __("Fiscal Year"),
            fieldtype: "Link",
            options: "Fiscal Year",
            default: frappe.defaults.get_user_default("fiscal_year"),
            reqd: 1,
            on_change: function(query_report) {
                set_fiscal_year_dates(query_report);
            }
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date"
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date"
        },
        {
            fieldname: "budget_against",
            label: __("Budget Against"),
            fieldtype: "Select",
            options: ["", "Cost Center"],
            default: "Cost Center",
            reqd: 1
        },
        {
            fieldname: "from_cc",
            label: __("From Cost Center"),
            fieldtype: "Link",
            options: "Cost Center",
            get_query: function() {
                return {
                    filters: {
                        disabled: 0
                    }
                };
            }
        },
        {
            fieldname: "from_acc",
            label: __("From Account"),
            fieldtype: "Link",
            options: "Account",
            get_query: function() {
                return {
                    filters: {
                        disabled: 0
                    }
                };
            }
        },
        {
            fieldname: "to_cc",
            label: __("To Cost Center"),
            fieldtype: "Link",
            options: "Cost Center",
            get_query: function() {
                return {
                    filters: {
                        disabled: 0
                    }
                };
            }
        },
        {
            fieldname: "to_acc",
            label: __("To Account"),
            fieldtype: "Link",
            options: "Account",
            get_query: function() {
                return {
                    filters: {
                        disabled: 0
                    }
                };
            }
        }
    ],

    onload: function(query_report) {
        set_fiscal_year_dates(query_report);
    }
};


function set_fiscal_year_dates(query_report) {
    var fiscal_year = query_report.get_filter_value("fiscal_year");

    if (!fiscal_year) {
        return;
    }

    frappe.call({
        method: "frappe.client.get_value",
        args: {
            doctype: "Fiscal Year",
            filters: {
                name: fiscal_year
            },
            fieldname: ["year_start_date", "year_end_date"]
        },
        callback: function(r) {
            if (!r.message) {
                return;
            }

            var from_date_filter = query_report.get_filter("from_date");
            var to_date_filter = query_report.get_filter("to_date");

            if (from_date_filter) {
                from_date_filter.set_value(r.message.year_start_date);
            }

            if (to_date_filter) {
                to_date_filter.set_value(r.message.year_end_date);
            }

            query_report.refresh();
        }
    });
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
