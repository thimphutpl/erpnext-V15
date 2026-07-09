# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	if not filters:
		filters = {}
	columns = [
		# {"label": "No.", "fieldname": "idx", "fieldtype": "Int", "width": 50},
		{"label": "Account", "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 150},
		{"label": "Actual Expenditure", "fieldname": "debit_in_account_currency", "fieldtype": "Data", "width": 200},
		{"label": "Revised Budget", "fieldname": "budget_amount", "fieldtype": "Data", "width": 200},
		{"label": "Proposed Budget", "fieldname": "initial_budget", "fieldtype": "Data", "width": 180},
		{"label": "Approved Budget", "fieldname": "approved_budget", "fieldtype": "Data", "width": 180},
		{"label": "Difference Amount", "fieldname": "difference_amount", "fieldtype": "Data", "width": 200},
		{"label": "Difference in Percent(%)", "fieldname": "difference_in_percent", "fieldtype": "Percent", "width": 150},
		{"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
		{"label": "Fiscal Year", "fieldname": "fiscal_year", "fieldtype": "Link", "options": "Fiscal Year", "width": 150},
	]
	conditions = []
	values = []

	if filters.get("company"):
		conditions.append("b.company = %s")
		values.append(filters.get("company"))

	if filters.get("fiscal_year"):
		conditions.append("b.fiscal_year = %s")
		values.append(filters.get("fiscal_year"))

	if filters.get("account"):
		conditions.append("ba.account = %s")
		values.append(filters.get("account"))		

	where_clause = " AND ".join(conditions)
	
	# Base query without f-string formatting
	query = """
		SELECT
			b.company,
			b.fiscal_year,
			ba.account,
			SUM(IFNULL(ba.initial_budget, 0)) as initial_budget,
			SUM(IFNULL(ba.approved_budget, 0)) as approved_budget,
			SUM(IFNULL(bra.budget_amount, 0)) as budget_amount,
			SUM(IFNULL(jea.debit_in_account_currency, 0)) as debit_in_account_currency
		FROM
			`tabBudget` b
		JOIN
			`tabBudget Account` ba
				ON ba.parent = b.name
		LEFT JOIN
			`tabBudget Release` br
				ON br.budget_id = b.name
		LEFT JOIN
			`tabBudget Release Account` bra
				ON bra.parent = br.name		
		LEFT JOIN
			`tabJournal Entry` je
				ON je.account = bra.account
		LEFT JOIN
			`tabJournal Entry Account` jea
				ON jea.parent = je.name
	"""
	
	if where_clause:
		query += f" WHERE {where_clause}"
	
	query += """
		GROUP BY
			b.company,
			b.fiscal_year,
			ba.account
	"""
	
	# Execute query - pass None if no values, otherwise pass the tuple
	if values:
		data = frappe.db.sql(query, tuple(values), as_dict=True)
	else:
		data = frappe.db.sql(query, as_dict=True)
	
	for idx, row in enumerate(data, start=1):
		row["idx"] = idx
		
		proposed_budget = row.get("initial_budget") or 0
		approved_budget = row.get("approved_budget") or 0
		revised_budget = row.get("budget_amount") or 0
		
		# Calculate difference: Proposed Budget - Revised Budget
		row["difference_amount"] = proposed_budget - revised_budget
		
		# Calculate percentage
		if proposed_budget != 0:
			row["difference_in_percent"] = (row["difference_amount"] / proposed_budget) * 100
		else:
			row["difference_in_percent"] = 0
		
		# Use the actual debit value as actual expenditure
		row["actual_expenditure"] = row.get("debit_in_account_currency") or 0

	return columns, data