// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Budget Release Report"] = {
    "filters": [

        {
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            options: "Company",
            "on_change": function (query_report) {
                set_program_code(query_report);
            }
            
        },

        {
            fieldname: "fiscal_year",
            label: "Fiscal Year",
            fieldtype: "Link",
            options: "Fiscal Year"
        },

        {
            fieldname: "month",
            label: "Month",
            fieldtype: "Select",
            options: [
                "",
                "July","August","September","October","November","December",
                "January","February","March","April","May","June"
            ]
        },

        {
            fieldname: "branch",
            label: "Branch",
            fieldtype: "Link",
            options: "Branch"
        },

        {
            fieldname: "cost_center",
            label: "Cost Center",
            fieldtype: "Link",
            options: "Cost Center"
        },

        {
            fieldname: "account",
            label: "Account",
            fieldtype: "Link",
            options: "Account"
        },

        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date"
        },

        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date"
        }

    ]

    
};

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
