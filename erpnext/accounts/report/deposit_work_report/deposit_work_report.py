# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "label":"Company",
            "fieldname":"company",
            "fieldtype":"Data",
             "width": 150

        },
         {
            "label":"Fiscal Year",
            "fieldname":"fiscal_year",
            "fieldtype":"Data",
             "width": 80

        },
         {
            "label":"Broad Head",
            "fieldname":"broad_head",
            "fieldtype":"Data",
             "width": 120

        },
        {
            "label":"Branch",
            "fieldname":"branch",
            "fieldtype":"Data",
             "width": 120

        },
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": "Journal Entry", "fieldname": "journal_entry", "fieldtype": "Link", "options": "Journal Entry", "width": 180},
        {"label": "Account", "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 200},
        {"label": "Debit", "fieldname": "debit", "fieldtype": "Currency", "width": 120},
        {"label": "Credit", "fieldname": "credit", "fieldtype": "Currency", "width": 120}
    ]

def get_data(filters):
    if not filters:
        filters = {}

    conditions = """
   
    """

    if filters.get("account"):
        conditions += " AND je.account = %(account)s"
    if filters.get("from_date"):
        conditions += " AND je.posting_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND je.posting_date <= %(to_date)s"
    if filters.get("company"):
        conditions += " AND je.company = %(company)s"
    if filters.get("broad_head"):
        conditions += " AND jea.broad_head = %(broad_head)s"
    if filters.get("branch"):
        conditions += " AND j.branch = %(branch)s"
    if filters.get("fiscal_year"):
        conditions += " AND je.fiscal_year = %(fiscal_year)s"

    data = frappe.db.sql(
        f"""
        SELECT
            je.posting_date,
            je.voucher_no AS journal_entry,
            je.account,
            acc.account_name,
            acc.parent_account,
            je.debit_in_account_currency AS debit,
            je.credit_in_account_currency AS credit,
            je.company as company,
            jea.broad_head as broad_head,
            j.branch as branch,
            je.fiscal_year as fiscal_year

        FROM
            `tabGL Entry` je
        INNER JOIN
            `tabJournal Entry Account` jea
            ON jea.parent = je.voucher_no
        INNER JOIN
            `tabJournal Entry` j
            ON j.name= je.voucher_no
        INNER JOIN
            `tabAccount` acc
            ON acc.name = je.account
            AND jea.account = je.account
        

        WHERE
            je.docstatus = 1
            AND
            acc.is_deposit_work = 1
            AND je.is_cancelled=0
            {conditions}

        ORDER BY
            je.posting_date ASC
        """,
        filters,
        as_dict=1,
    )

    return data