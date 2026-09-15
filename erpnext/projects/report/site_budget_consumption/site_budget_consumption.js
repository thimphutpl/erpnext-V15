// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// frappe.query_reports["Site Budget Consumption"] = {
// 	"filters": [

// 	]
// };


frappe.query_reports["Site Budget Consumption"] = {
    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: "GYALSUNG INFRA",
            reqd: 1,
        },

        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: "2020-01-01",
            reqd: 1,
            read_only: 1,
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1,
            read_only: 1,
        }
    ],
};
