# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_columns(filters):
	return [
		{
			"label": "Employee",
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 120,
		},
		{
			"label": "Employee Name",
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"label": "Cost Center",
			"fieldname": "cost_center",
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 120
		},
		{
			"label": "Posting Date",
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": "Account",
			"fieldname": "account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 180,
		},
		{
			"label": "Advance Amount",
			"fieldname": "advance_amount",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": "Paid Amount",
			"fieldname": "paid_amount",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": "Total Outstanding",
			"fieldname": "total_outstanding",
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"label": "Voucher Type",
			"fieldname": "voucher_type",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			
			"label": "Voucher No",
			"fieldname": "voucher_no",
			"fieldtype": "Link",
			"options": "Journal Entry",
			"width": 120
		}
	]


def get_data(filters):
	
  


	conditions = []
	values = []

	if filters.get("fiscal_year"):
		conditions.append("gl.fiscal_year = %s")
		values.append(filters.get("fiscal_year"))

	if filters.get("from_date") and filters.get("to_date"):
		conditions.append("gl.posting_date BETWEEN %s AND %s")
		values.extend([filters.get("from_date"), filters.get("to_date")])

	if filters.get("company"):
		conditions.append("gl.company = %s")
		values.append(filters.get("company"))

	if filters.get("employee"):
		conditions.append("gl.party = %s")
		values.append(filters.get("employee"))

	conditions.append("gl.against_voucher_type = 'Employee Advance'")
	conditions.append("gl.is_cancelled = 0")

	where_clause = " AND ".join(conditions)

	query = f"""
		SELECT
			gl.party AS employee,
			emp.employee_name ,
			gl.cost_center,
			gl.posting_date  ,
			gl.account ,
			gl.debit AS advance_amount,
			gl.credit AS paid_amount,
			gl.debit - gl.credit AS total_outstanding,
			gl.voucher_type,
			gl.voucher_no

		FROM `tabGL Entry` gl

		LEFT JOIN `tabEmployee` emp
			ON emp.name = gl.party

		WHERE {where_clause}
		ORDER BY
			gl.posting_date ASC,
			gl.voucher_no ASC
	"""

	return frappe.db.sql(query, values, as_dict=True)