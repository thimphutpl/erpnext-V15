// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Deposit Work Report"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company")


        },
        {
            "fieldname": "fiscal_year",
            "label": "Fiscal Year",
            "fieldtype": "Link",
            "options": "Fiscal Year",



        },
        {
            "fieldname": "broad_head",
            "label": "Broad Head",
            "fieldtype": "Link",
            "options": "Account",
            get_query: function () {
                return {
                    filters: {
                        is_deposit_work: 1,
                        company: frappe.query_report.get_filter_value("company")
                    }
                };
            }


        },
        {
            "fieldname": "branch",
            "label": "Branch",
            "fieldtype": "Link",
            "options": "Branch",
            get_query: function () {
                return {
                    filters: {
                        disabled: 0,
                        company: frappe.query_report.get_filter_value("company")
                    }
                };
            }


        },
        {
            "fieldname": "account",
            "label": "Account",
            "fieldtype": "Link",
            "options": "Account",
            get_query: function () {
                return {
                    filters: {
                        is_deposit_work: 1,
                        company: frappe.query_report.get_filter_value("company")

                    }
                };
            }
        },
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "default": frappe.datetime.month_start()
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.month_end()
        }
    ]
}
