# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
    validate_filters(filters)
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def validate_filters(filters):
    if not filters:
        frappe.throw("Filters are required.")
    if not filters.get("from_date") or not filters.get("to_date"):
        frappe.throw("Please provide From Date and To Date.")

def get_data(filters=None):
    gl_cond = "and gl.account = %s" if filters.account else ""
    query = f"""
        SELECT 
            p.name AS project, 
            p.cost_center, 
            p.project_definition, 
            SUM(COALESCE(gl.debit, 0)) AS expense, 
            SUM(COALESCE(gl.credit, 0)) AS income
        FROM `tabProject` p
        LEFT JOIN `tabGL Entry` gl ON gl.project = p.name
        LEFT JOIN `tabAccount` acc ON acc.name = gl.account
        WHERE p.docstatus != 2
        AND acc.root_type = 'Expense'
        AND gl.is_cancelled = 0
		AND p.project_definition = %s
        AND gl.posting_date BETWEEN %s AND %s
        {gl_cond}
        GROUP BY p.name
    """
    params = [filters.project_definition, filters.from_date, filters.to_date]
    if filters.account:
        params.append(filters.account)

    data = frappe.db.sql(query, tuple(params), as_dict=True)
    return [
        build_row(row, filters)
        for row in data
    ]

def build_row(raw, filters):
    total_expense = flt(raw.expense or 0) - flt(raw.income or 0)
    return frappe._dict({
        "cost_center": raw.cost_center,
        "project": raw.project,
        "expense": raw.expense or 0,
        "income": raw.income or 0,
        "total_expense": total_expense,
        "from_date": filters.from_date,
        "to_date": filters.to_date
    })

COLUMN_DEFINITIONS = [
    {"fieldname": "cost_center", "fieldtype": "Link", "width": 250, "label": "Cost Center", "options": "Cost Center"},
    {"fieldname": "project", "fieldtype": "Link", "width": 350, "label": "Project", "options": "Project"},
    {"fieldname": "expense", "fieldtype": "Data", "width": 150, "label": "Expense"},
    {"fieldname": "income", "fieldtype": "Data", "width": 150, "label": "Income"},
    {"fieldname": "total_expense", "fieldtype": "Data", "width": 150, "label": "Total Expense"},
    {"fieldname": "from_date", "fieldtype": "Date", "width": 120, "label": "From Date"},
    {"fieldname": "to_date", "fieldtype": "Date", "width": 120, "label": "To Date"}
]

def get_columns():
    return COLUMN_DEFINITIONS