# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	if not filters:
		filters = {}
	columns = [
		{"label": "Account", "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 150},
		{"label": "Cost Center", "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
		{"label": "Current Expenditure", "fieldname": "current_expenditure", "fieldtype": "Currency", "width": 200},
		{"label": "Capital Expenditure", "fieldname": "capital_expenditure", "fieldtype": "Currency", "width": 200},
		{"label": "Lending Expenditure", "fieldname": "lending_expenditure", "fieldtype": "Currency", "width": 180},
		{"label": "Repayment Expenditure", "fieldname": "repayment_expenditure", "fieldtype": "Currency", "width": 180},
		{"label": "Total", "fieldname": "total_amount", "fieldtype": "Currency", "width": 200},
		{"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
		{"label": "Fiscal Year", "fieldname": "fiscal_year", "fieldtype": "Link", "options": "Fiscal Year", "width": 150},
	]
	conditions = []
	values = []

	if filters.get("company"):
		conditions.append("je.company = %s")
		values.append(filters.get("company"))

	if filters.get("fiscal_year"):
		conditions.append("je.fiscal_year = %s")
		values.append(filters.get("fiscal_year"))

	if filters.get("account"):
		conditions.append("je.account = %s")
		values.append(filters.get("account"))	

	where_clause = " AND ".join(conditions)
	
	query = """
		SELECT
			je.company,
			je.fiscal_year,
			je.cost_center,
			je.account,
			SUM(CASE 
				WHEN acc.parent_account LIKE '10 a - Current - RBA%%' 
				THEN IFNULL(je.debit_in_account_currency, 0)
				ELSE 0 
			END) as current_expenditure,
			SUM(CASE 
				WHEN acc.parent_account LIKE '10 b - Capital - RBA%%' 
				THEN IFNULL(je.debit_in_account_currency, 0)
				ELSE 0 
			END) as capital_expenditure,
			SUM(CASE 
				WHEN acc.parent_account LIKE '10 c - Lending - RBA%%' 
				THEN IFNULL(je.debit_in_account_currency, 0)
				ELSE 0 
			END) as lending_expenditure,
			SUM(CASE 
				WHEN acc.parent_account LIKE '10 d - Repayment - RBA%%' 
				THEN IFNULL(je.debit_in_account_currency, 0)
				ELSE 0 
			END) as repayment_expenditure
		FROM
			`tabGL Entry` je
		LEFT JOIN
			`tabAccount` acc
				ON acc.name = je.account
	"""
	
	if where_clause:
		query += f" WHERE {where_clause}"
	
	query += """
		GROUP BY
			je.company,
			je.fiscal_year,
			je.cost_center
	"""
	
	if values:
		data = frappe.db.sql(query, tuple(values), as_dict=True)
	else:
		data = frappe.db.sql(query, as_dict=True)
	
	for idx, row in enumerate(data, start=1):
		row["idx"] = idx
		
		current_exp = row.get("current_expenditure") or 0
		capital_exp = row.get("capital_expenditure") or 0
		lending_exp = row.get("lending_expenditure") or 0
		repayment_exp = row.get("repayment_expenditure") or 0
		
		# Calculate total
		row["total_amount"] = current_exp + capital_exp + lending_exp + repayment_exp

	return columns, data