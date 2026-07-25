// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Budget Variance Report"] = {
    filters: get_filters(),
    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname.includes(__("variance"))) {
            if (data[column.fieldname] < 0) {
                value = "<span style='color:red'>" + value + "</span>";
            } else if (data[column.fieldname] > 0) {
                value = "<span style='color:green'>" + value + "</span>";
            }
        }

        return value;
    },
};
function get_filters() {
    function get_dimensions() {
        let result = [];
        frappe.call({
            method: "erpnext.accounts.doctype.accounting_dimension.accounting_dimension.get_dimensions",
            args: {
                with_cost_center_and_project: true,
            },
            async: false,
            callback: function (r) {
                if (!r.exc) {
                    result = r.message[0].map((elem) => elem.document_type);
                }
            },
        });
        return result;
    }

    let budget_against_options = get_dimensions();

    let filters = [

        {
            fieldname: "fiscal_year",
            label: __("Fiscal Year"),
            fieldtype: "Link",
            options: "Fiscal Year",
            default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today()),
            reqd: 1,
        },
        // {
        //     fieldname: "period",
        //     label: __("Period"),
        //     fieldtype: "Select",
        //     options: [
        //         { value: "Monthly", label: __("Monthly") },
        //         { value: "Quarterly", label: __("Quarterly") },
        //         { value: "Half-Yearly", label: __("Half-Yearly") },
        //         { value: "Yearly", label: __("Yearly") },
        //     ],
        //     default: "Yearly",
        //     reqd: 1,
        // },
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company"),
            reqd: 1,
            "on_change": function (query_report) {
                set_program_code(query_report);
            }
        },
        {
            fieldname: "budget_against",
            label: __("Budget Against"),
            fieldtype: "Select",
            options: budget_against_options,
            default: "Cost Center",
            reqd: 1,

        },
        {
            fieldname: "type",
            label: "Type",
            fieldtype: "Select",
            options: [
                "Proposed Budget",
                "Approved Budget",
                "Current Budget"
            ],
            default: "Approved Budget"
        },
        // {
        //     fieldname: "budget_against_filter",
        //     label: __("Dimension Filter"),
        //     fieldtype: "MultiSelectList",
        //     get_data: function (txt) {
        //         if (!frappe.query_report.filters) return;

        //         let budget_against = frappe.query_report.get_filter_value("budget_against");
        //         if (!budget_against) return;

        //         return frappe.db.get_link_options(budget_against, txt);
        //     },
        // },
        // {
        //     fieldname: "show_cumulative",
        //     label: __("Show Cumulative Amount"),
        //     fieldtype: "Check",
        //     default: 0,
        // },
    ];

    return filters;
}
function set_program_code(report) {

    let company = report.get_filter_value("company");

    if (!company) {
        report.program_code = "";
        report.program_name = "";

        frappe.query_report.load();
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

        if (r.message) {

            report.program_code = r.message.program_code || "";
            report.program_name = r.message.program_name || "";

        } else {

            report.program_code = "";
            report.program_name = "";

        }

        frappe.query_report.load();

    });
}