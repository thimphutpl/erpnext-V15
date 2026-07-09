# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	if not filters:
		filters = {}
	columns = [
		{"label": "Account", "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 150},
		{"label": "Receipt Cash Amount", "fieldname": "cash_amount", "fieldtype": "Currency", "width": 200},
		{"label": "Receipt Bank Amount", "fieldname": "bank_amount", "fieldtype": "Currency", "width": 200},
		{"label": "Total Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 200},
		{"label": "Payment Cash Amount", "fieldname": "payment_cash_amount", "fieldtype": "Currency", "width": 200},
		{"label": "Payment Bank Amount", "fieldname": "payment_bank_amount", "fieldtype": "Currency", "width": 200},
		{"label": "Total Amount", "fieldname": "payment_total_amount", "fieldtype": "Currency", "width": 200},
		{"label": "Cheque Number", "fieldname": "cheque_no", "fieldtype": "Data", "width": 200},
		{"label": "Cost Center", "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
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

	# Add condition to filter only Cash and Bank accounts
	conditions.append("(acc.parent_account LIKE '12 a - Cash - RBA%%' OR acc.parent_account LIKE '12 b - Bank - RBA%%')")
	
	where_clause = " AND ".join(conditions)
	
	query = """
		SELECT
			j.cheque_no,
			je.company,
			je.fiscal_year,
			je.cost_center,
			je.account,
			SUM(CASE 
				WHEN acc.parent_account LIKE '12 a - Cash - RBA%%' 
				THEN IFNULL(je.debit_in_account_currency, 0)
				ELSE 0 
			END) as cash_amount,
			SUM(CASE 
				WHEN acc.parent_account LIKE '12 b - Bank - RBA%%' 
				THEN IFNULL(je.debit_in_account_currency, 0)
				ELSE 0 
			END) as bank_amount,
			SUM(CASE 
				WHEN acc.parent_account LIKE '12 a - Cash - RBA%%' 
				THEN IFNULL(je.credit_in_account_currency, 0)
				ELSE 0 
			END) as payment_cash_amount,
			SUM(CASE 
				WHEN acc.parent_account LIKE '12 b - Bank - RBA%%' 
				THEN IFNULL(je.credit_in_account_currency, 0)
				ELSE 0 
			END) as payment_bank_amount
		FROM
			`tabGL Entry` je
		LEFT JOIN
			`tabAccount` acc
				ON acc.name = je.account
		LEFT JOIN
			`tabJournal Entry` j
				ON j.name = je.voucher_no		
	"""
	
	if where_clause:
		query += f" WHERE {where_clause}"
	
	query += """
		GROUP BY
			je.company,
			je.fiscal_year,
			je.cost_center,
			je.account
	"""
	
	if values:
		data = frappe.db.sql(query, tuple(values), as_dict=True)
	else:
		data = frappe.db.sql(query, as_dict=True)
	
	for idx, row in enumerate(data, start=1):
		row["idx"] = idx
		
		cash_amt = row.get("cash_amount") or 0
		bank_amt = row.get("bank_amount") or 0

		p_cash_amt = row.get("payment_cash_amount") or 0
		p_bank_amt = row.get("payment_bank_amount") or 0
		
		# Calculate total
		row["total_amount"] = cash_amt + bank_amt
		row["payment_total_amount"] = p_cash_amt + p_bank_amt

	return columns, data