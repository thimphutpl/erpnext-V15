// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Receipts and Payments Statement"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "reqd": 0,
            // "default": frappe.datetime.get_month_start()
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "reqd": 0,
            // "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "fiscal_year",
            "label": "Fiscal Year",
            "fieldtype": "Link",
            "options": "Fiscal Year",
            "reqd": 0
        },
        {
            "fieldname": "company",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 0,
            "default": frappe.defaults.get_user_default("Company")
        },
        {
            "fieldname": "account",
            "label": "Account",
            "fieldtype": "Link",
            "options": "Account",
            "reqd": 0
        }
    ],

    // Optional: Add formatter for better visualization
    "formatter": function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        // Color code the total amount
        if (column.fieldname == "total_amount") {
            if (value > 0) {
                value = "<span style='color:green; font-weight:bold'>" + value + "</span>";
            } else if (value < 0) {
                value = "<span style='color:red; font-weight:bold'>" + value + "</span>";
            }
        }

        // Color code receipt and payment amounts
        if (column.fieldname == "receipt_amount" && value > 0) {
            value = "<span style='color:green'>" + value + "</span>";
        }
        if (column.fieldname == "payment_amount" && value > 0) {
            value = "<span style='color:red'>" + value + "</span>";
        }

        return value;
    }
};