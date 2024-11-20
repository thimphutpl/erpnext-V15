# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data
def get_columns():
		return[
			("Name of Work") + "Data:200",
			("Type of Work") + "Data:150",
			("Customer") + "Data:150",
			("Recieved Amount") + "Currency:100",
			("Expense Amount") + "Currency: 100",
			("Balance") + "Currency:100",
			("From Date") + "Date: 100",
			("To Date") + "Date:100"

	]

def get_data(filters):
	query = """SELECT name_of_work,
	work_type,
	 customer,
	 total_received_amount,
	 total_expense_amount,
	  balance_amount,
	start_date,
	end_date
	FROM `tabDeposit Work`
	where docstatus = 0 """

	if filters.get("branch"):
		query += "and branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		query += "and end_date between \'" + str(filters.from_date) +"\' and \' " + str(filters.to_date) +"\'"
	return frappe.db.sql(query)
