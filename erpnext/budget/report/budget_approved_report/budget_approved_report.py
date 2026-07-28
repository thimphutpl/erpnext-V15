# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
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
            "width": 100
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
            "label": _("Cost Center"),
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
            "fieldname": "parent_account",
            "label": _("Parent Account"),
            "fieldtype": "Link",
            "options": "Account",
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
            "label": _("Source Of Fund"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "source_of_fund_name",
            "label": _("Source of Fund Name"),
            "fieldtype": "Data",
            "width": 120
        },

        {
            "fieldname": "account_initial_budget",
            "label": _("Initial Budget"),
            "fieldtype": "Currency",
            "width": 130
        },


        {
            "fieldname": "current_budget",
            "label": _("Current"),
            "fieldtype": "Currency",
            "width": 120
        },


        {
            "fieldname": "capital_budget",
            "label": _("Capital"),
            "fieldtype": "Currency",
            "width": 120
        },


        {
            "fieldname": "lending_budget",
            "label": _("Lending"),
            "fieldtype": "Currency",
            "width": 120
        },


        {
            "fieldname": "repayment_budget",
            "label": _("Repayment"),
            "fieldtype": "Currency",
            "width": 120
        },


        {
            "fieldname": "total_budget",
            "label": _("Total"),
            "fieldtype": "Currency",
            "width": 120
        },


        {
            "fieldname": "supplementary_budget",
            "label": _("Supplementary Budget"),
            "fieldtype": "Currency",
            "width": 130
        },


        {
            "fieldname": "budget_received",
            "label": _("Budget Received"),
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "fieldname": "remarks",
            "label": _("Remarks"),
            "fieldtype": "Small Text",
            "width": 130
        }

    ]


def get_data(filters):

    conditions = get_conditions(filters)


    query = """

        SELECT

            b.company,
            b.branch,
            b.posting_date,
            b.cost_center AS budget_cost_center,
            b.fiscal_year,


            ba.account,
            ba.account_number,
            ba.initial_budget AS account_initial_budget,
            ba.budget_amount,
            ba.supplementary_budget,
            ba.budget_received,
            ba.remarks,


            ba.source_of_fund,
            sof.source_of_fund as source_of_fund_name,
            ba.budget_activity,
            ba.budget_sub_activity,


            acc.parent_account,
            acc.account_name,


            CASE
                WHEN acc.parent_account LIKE '10 a%%'
                THEN COALESCE(ba.approved_budget)
                ELSE 0
            END AS current_budget,

            CASE
                WHEN acc.parent_account LIKE '10 b%%'
                THEN COALESCE(ba.approved_budget)
                ELSE 0
            END AS capital_budget,

            CASE
                WHEN acc.parent_account LIKE '10 c%%'
                THEN COALESCE(ba.approved_budget)
                ELSE 0
            END AS lending_budget,

            CASE
                WHEN acc.parent_account LIKE '10 d%%'
                THEN COALESCE(ba.approved_budget)
                ELSE 0
            END AS repayment_budget



        FROM `tabBudget Proposal` b


        INNER JOIN `tabBudget Proposal Account` ba
            ON b.name = ba.parent
        INNER JOIN `tabAccount` acc
            ON ba.account = acc.name


        INNER JOIN `tabSource of Fund` sof
            ON ba.source_of_fund = sof.name



        {conditions}


        ORDER BY
            b.cost_center,
            ba.budget_activity,
            ba.budget_sub_activity,
            ba.source_of_fund,
            ba.account


            

    """.format(
        conditions=conditions
    )


    data = frappe.db.sql(
        query,
        filters,
        as_dict=True
    )


    for row in data:

        row.total_budget = (
            (row.current_budget or 0)
            +
            (row.capital_budget or 0)
            +
            (row.lending_budget or 0)
            +
            (row.repayment_budget or 0)
        )


    return data



def get_conditions(filters):

    conditions = []


    if filters.get("company"):
        conditions.append(
            "b.company = %(company)s"
        )


    if filters.get("branch"):
        conditions.append(
            "b.branch = %(branch)s"
        )


    if filters.get("fiscal_year"):
        conditions.append(
            "b.fiscal_year = %(fiscal_year)s"
        )


    if filters.get("cost_center"):
        conditions.append(
            """
            (
                b.cost_center = %(cost_center)s
                OR
                ba.cost_center = %(cost_center)s
            )
            """
        )


    if filters.get("account"):
        conditions.append(
            "ba.account = %(account)s"
        )


    if filters.get("source_of_fund"):
        conditions.append(
            "ba.source_of_fund = %(source_of_fund)s"
        )


    if filters.get("budget_activity"):
        conditions.append(
            "ba.budget_activity = %(budget_activity)s"
        )


    if filters.get("budget_sub_activity"):
        conditions.append(
            "ba.budget_sub_activity = %(budget_sub_activity)s"
        )


    if filters.get("budget_name"):
        conditions.append(
            "b.name = %(budget_name)s"
        )


    if filters.get("parent_account"):
        conditions.append(
            "acc.parent_account = %(parent_account)s"
        )


    if conditions:
        return " AND " + " AND ".join(conditions)

    return ""