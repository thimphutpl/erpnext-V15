# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe

# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data

import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": _("Budget Release"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Budget Release",
            "width": 180
        },
        {
            "label": _("Company"),
            "fieldname": "company",
            "fieldtype": "Link",
            "options": "Company",
            "width": 150
        },
        {
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": _("Fiscal Year"),
            "fieldname": "fiscal_year",
            "fieldtype": "Link",
            "options": "Fiscal Year",
            "width": 120
        },
        {
            "label": _("Month"),
            "fieldname": "month",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Branch"),
            "fieldname": "branch",
            "fieldtype": "Link",
            "options": "Branch",
            "width": 150
        },
        {
            "label": _("Cost Center"),
            "fieldname": "cost_center",
            "fieldtype": "Link",
            "options": "Cost Center",
            "width": 150
        },
        {
            "label": _("Account"),
            "fieldname": "account",
            "fieldtype": "Link",
            "options": "Account",
            "width": 220
        },
        {
            "label": _("Budget Activity"),
            "fieldname": "budget_activity",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Budget Sub Activity"),
            "fieldname": "budget_sub_activity",
            "fieldtype": "Data",
            "width": 220
        },
        {
            "label": _("Source of Fund"),
            "fieldname": "source_of_fund",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Approved Budget"),
            "fieldname": "approved_budget",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": _("Released Budget"),
            "fieldname": "released_budget",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": _("Current Balance"),
            "fieldname": "current_balance",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": _("Budget Balance"),
            "fieldname": "budget_balance",
            "fieldtype": "Currency",
            "width": 150
        },
    ]


def get_data(filters):

    conditions = get_conditions(filters)

    query = f"""
        SELECT
            b.name,
            b.company,
            b.posting_date,
            b.fiscal_year,
            b.month,
            b.branch,
            b.cost_center,
            ba.account,
            ba.budget_activity,
            ba.budget_sub_activity,
            ba.source_of_fund,
            ba.approved_budget,
            ba.released_budget,
            b.current_balance,
            b.budget_balance
        FROM `tabBudget Release` b
        INNER JOIN `tabBudget Release Account` ba
            ON ba.parent = b.name
        WHERE b.docstatus = 1
        {conditions}
        ORDER BY b.posting_date DESC
    """

    return frappe.db.sql(query, filters, as_dict=True)


def get_conditions(filters):
    conditions = []

    if filters.get("company"):
        conditions.append("b.company = %(company)s")

    if filters.get("fiscal_year"):
        conditions.append("b.fiscal_year = %(fiscal_year)s")

    if filters.get("month"):
        conditions.append("b.month = %(month)s")

    if filters.get("branch"):
        conditions.append("b.branch = %(branch)s")

    if filters.get("cost_center"):
        conditions.append("b.cost_center = %(cost_center)s")

    if filters.get("account"):
        conditions.append("ba.account = %(account)s")

    if filters.get("from_date"):
        conditions.append("b.posting_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("b.posting_date <= %(to_date)s")

    return " AND " + " AND ".join(conditions) if conditions else ""
