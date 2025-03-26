// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Expenditure Statement"] = erpnext.financial_statements;

// Ensure filters array exists
frappe.query_reports["Expenditure Statement"].filters = frappe.query_reports["Expenditure Statement"].filters || [];

frappe.query_reports["Expenditure Statement"].filters.push(
    {
        "fieldname": "accumulated_values",
        "label": __("Accumulated Values"),
        "fieldtype": "Check"
    },
    {
        "fieldname": "show_zero_values",
        "label": __("Show zero values"),
        "fieldtype": "Check"
    }
);

