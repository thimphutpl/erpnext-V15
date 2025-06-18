# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns():
        return[
		("Employee") + ":Link/Employee:120",
		("Employee Name") + ":Data:120",
                ("Bank Name") + ":Data:120",
		("Bank Account") + ":Data:120",
                ("Total Amount") + ":Currency:120",
		("OT Ref") + ":Link/Process Overtime Payment:120"
        ]

def get_data(filters):
	# Build base query and parameters
	query = """ select oti.employee, oti.employee_name, oti.bank_name, oti.bank_account, sum(oti.total_ot_amount) as total_ot_amount, ot.name \
		from `tabProcess Overtime Payment` ot, `tabOvertime Payment Item` oti where oti.parent = ot.name \
		and ot.docstatus <= 1"""
	params = []

	if filters.get("ot_reference"):
		query += " and ot.name = %s"
		params.append(filters["ot_reference"])

	if filters.get("branch"):
		query += " and ot.branch = %s"
		params.append(filters["branch"])

	if filters.get("from_date") and filters.get("to_date"):
		query += " and ot.posting_date between %s and %s"
		params.extend([filters["from_date"], filters["to_date"]])

	# Group by all non-aggregated columns
	query += " group by oti.employee, oti.employee_name, oti.bank_name, oti.bank_account, ot.name"
	return frappe.db.sql(query, params)
