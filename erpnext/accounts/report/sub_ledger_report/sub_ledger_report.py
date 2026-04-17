# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": "Journal Entry", "fieldname": "journal_entry", "fieldtype": "Link", "options": "Journal Entry", "width": 180},
        {"label": "Account", "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 200},
        {"label": "Debit", "fieldname": "debit", "fieldtype": "Currency", "width": 120},
        {"label": "Credit", "fieldname": "credit", "fieldtype": "Currency", "width": 120},
        {"label": "Remarks", "fieldname": "remarks", "fieldtype": "Data", "width": 250},
    ]


def get_data(filters):

    conditions = ""

    if filters.get("account"):
        conditions += " AND jea.account = %(account)s"

    if filters.get("from_date"):
        conditions += " AND je.posting_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND je.posting_date <= %(to_date)s"

    data = frappe.db.sql(
        f"""
        SELECT
            je.posting_date,
            je.name as journal_entry,
            jea.account,
            jea.debit_in_account_currency as debit,
            jea.credit_in_account_currency as credit,
            je.user_remark as remarks
        FROM
            `tabJournal Entry` je
        JOIN
            `tabJournal Entry Account` jea
        ON
            je.name = jea.parent
        WHERE
            je.docstatus = 1
            {conditions}
        ORDER BY
            je.posting_date ASC
        """,
        filters,
        as_dict=1,
    )

    return data
