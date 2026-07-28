// Copyright (c) 2026
// For license information, please see license.txt

frappe.query_reports["Outstanding Advances"] = {
    filters: [
        {
            fieldname: "fiscal_year",
            label: __("Fiscal Year"),
            fieldtype: "Link",
            options: "Fiscal Year",
            default: frappe.defaults.get_user_default("fiscal_year"),
            reqd: 1
        },
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company"),
            reqd: 1,

            on_change: async function (report) {
                await set_program_details(report);
                report.trigger_refresh();
            }
        },
        {
            fieldname: "customer",
            label: __("Party/Employee"),
            fieldtype: "Data"
        },
        {
            fieldname: "account",
            label: __("Account"),
            fieldtype: "Link",
            options: "Account",

            get_query: function () {
                return {
                    filters: {
                        is_group: 0,
                        disabled: 0
                    }
                };
            }
        },
        {
            fieldname: "budget_sub_activity",
            label: __("Budget Sub Activity"),
            fieldtype: "Link",
            options: "Budget Sub Activity"
        },
        {
            fieldname: "source_of_fund",
            label: __("Source of Fund"),
            fieldtype: "Link",
            options: "Source of Fund"
        }
    ],

    onload: async function (report) {
        await set_program_details(report);
    }
};


/**
 * Fetch Program Code and Program Name from the selected Company.
 *
 * These values can later be used inside the print format as:
 *
 * frappe.query_report.program_code
 * frappe.query_report.program_name
 */
async function set_program_details(report) {
    const company = report.get_filter_value("company");

    report.program_code = "";
    report.program_name = "";

    if (!company) {
        return;
    }

    try {
        const response = await frappe.db.get_value(
            "Company",
            company,
            [
                "program_code",
                "program_name"
            ]
        );

        const company_data = response.message || {};

        report.program_code =
            company_data.program_code || "";

        report.program_name =
            company_data.program_name || "";

    } catch (error) {
        console.error(
            "Unable to fetch Company program details:",
            error
        );

        report.program_code = "";
        report.program_name = "";
    }
}