# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data, None

def get_columns():
    return [
        {
            "fieldname": "company",
            "label": _("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "width": 120
        },
        {
            "fieldname": "posting_date",
            "label": _("Posting Date"),
            "fieldtype": "Date",
            "width": 120
        },
        
        {
            "fieldname": "branch",
            "label": _("Branch"),
            "fieldtype": "Link",
            "options": "Branch",
            "width": 120
        },
        {
            "fieldname": "fiscal_year",
            "label": _("Fiscal Year"),
            "fieldtype": "Link",
            "options": "Fiscal Year",
            "width": 100
        },
        {
            "fieldname": "budget_cost_center",
            "label": _("Budget Cost Center"),
            "fieldtype": "Link",
            "options": "Cost Center",
            "width": 150
        },
        {
            "fieldname": "budget_activity",
            "label": _("Budget Activity"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "budget_sub_activity",
            "label": _("Budget Sub Activity"),
            "fieldtype": "Data",
            "width": 250
        },
        {
            "fieldname": "account",
            "label": _("Account"),
            "fieldtype": "Link",
            "options": "Account",
            "width": 250
        },
        {
            "fieldname": "source_of_fund",
            "label": _("Source of Fund"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "account_initial_budget",
            "label": _("Initial Budget"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "approved_budget",
            "label": _("Approved Budget"),
            "fieldtype": "Currency",
            "width": 130
        },
        
        # {
        #     "fieldname": "initial_budget",
        #     "label": _("Total Proposed Budget"),
        #     "fieldtype": "Currency",
        #     "width": 130
        # },
        {
            "fieldname": "withdraw_budget",
            "label": _("Withdraw Budget"),
            "fieldtype": "Currency",
            "width": 120
        },
        # {
        #     "fieldname": "actual_total",
        #     "label": _("Actual Total"),
        #     "fieldtype": "Currency",
        #     "width": 120
        # },
        {
            "fieldname": "budget_amount",
            "label": _("Account Budget Amount"),
            "fieldtype": "Currency",
            "width": 150
        },
        
        {
            "fieldname": "supplementary_budget",
            "label": _("Supplementary Budget"),
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "fieldname": "budget_received",
            "label": _("Budget Received"),
            "fieldtype": "Currency",
            "width": 120
        },
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    
    query = """
        SELECT 
            b.company,
            b.branch,
            b.posting_date,
            b.cost_center as budget_cost_center,
            b.fiscal_year,
            ba.approved_budget,
            b.initial_budget,
            b.withdrawal_budget,
            b.actual_total,
            ba.account,
            ba.account_number,
            ba.budget_amount,
            ba.initial_budget as account_initial_budget,
            ba.supplementary_budget,
            ba.budget_received,
            ba.cost_center as account_cost_center,
            ba.source_of_fund,
            ba.budget_activity,
            ba.budget_sub_activity,
            b.name as budget_name,
            ba.name as budget_account_name
        FROM `tabBudget` b
        INNER JOIN `tabBudget Account` ba ON b.name = ba.parent
        {conditions}
        ORDER BY b.fiscal_year, ba.account_number, ba.account
    """.format(conditions=conditions)
    
    data = frappe.db.sql(query, filters, as_dict=1)
    return data

def get_conditions(filters):
    conditions = []
    
    if filters.get("company"):
        conditions.append("b.company = %(company)s")
        
    if filters.get("posting_date"):
        conditions.append("b.posting_date = %(posting_date)s")
    
    if filters.get("branch"):
        conditions.append("b.branch = %(branch)s")
    
    if filters.get("fiscal_year"):
        conditions.append("b.fiscal_year = %(fiscal_year)s")
    
    if filters.get("cost_center"):
        conditions.append("(b.cost_center = %(cost_center)s OR ba.cost_center = %(cost_center)s)")
    
    if filters.get("account"):
        conditions.append("ba.account = %(account)s")
    
    if filters.get("source_of_fund"):
        conditions.append("ba.source_of_fund = %(source_of_fund)s")
        
    if filters.get("approved_budget"):
        conditions.append("ba.approved_budget = %(approved_budget)s")
    
    if filters.get("budget_activity"):
        conditions.append("ba.budget_activity = %(budget_activity)s")

    if filters.get("budget_sub_activity"):
        conditions.append("ba.budget_sub_activity = %(budget_sub_activity)s")        
    
    if filters.get("budget_name"):
        conditions.append("b.name = %(budget_name)s")
    
    if filters.get("budget_account_name"):
        conditions.append("ba.name = %(budget_account_name)s")
    
    return " AND " + " AND ".join(conditions) if conditions else ""
