# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

# def execute(filters=None):
# 	columns = get_columns()
# 	data = get_data(filters)

# 	return columns, data
# def get_columns():
# 		return[
# 			("Name of Work") + "Data:200",
# 			("Type of Work") + "Data:150",
# 			("Customer") + "Data:150",
# 			("Recieved Amount") + "Currency:100",
# 			("Expense Amount") + "Currency: 100",
# 			("Balance") + "Currency:100",
# 			("From Date") + "Date: 100",
# 			("To Date") + "Date:100"

# 	]

# def get_data(filters):
# 	query = """SELECT name_of_work,
# 	work_type,
# 	 customer,
# 	 total_received_amount,
# 	 total_expense_amount,
# 	  balance_amount,
# 	start_date,
# 	end_date
# 	FROM `tabDeposit Work`
# 	where docstatus = 0 """

# 	if filters.get("branch"):
# 		query += "and branch = \'" + str(filters.branch) + "\'"

# 	if filters.get("from_date") and filters.get("to_date"):
# 		query += "and end_date between \'" + str(filters.from_date) +"\' and \' " + str(filters.to_date) +"\'"
# 	return frappe.db.sql(query)


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": "Journal Entry", "fieldname": "journal_entry", "fieldtype": "Link", "options": "Journal Entry", "width": 180},
        {"label": "Broad Head", "fieldname": "broad_head", "fieldtype": "Link", "options": "Account", "width": 200},
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
            jea.broad_head,
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
