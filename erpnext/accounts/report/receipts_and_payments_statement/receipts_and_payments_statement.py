# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, add_years

def execute(filters=None):
	if not filters:
		filters = {}
	columns = [
		{"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 150},
		{"label": "Account", "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 200},
		{"label": "Cost Center", "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
		{"label": "Monthly Receipts Amount", "fieldname": "receipt_amount", "fieldtype": "Currency", "width": 150},
		{"label": "Annual Receipts Amount", "fieldname": "annual_receipt_amount", "fieldtype": "Currency", "width": 180},
		{"label": "Monthly Payments Amount", "fieldname": "payment_amount", "fieldtype": "Currency", "width": 150},
		{"label": "Annual Payments Amount", "fieldname": "annual_payment_amount", "fieldtype": "Currency", "width": 180},
		{"label": "Total", "fieldname": "total_amount", "fieldtype": "Currency", "width": 150},
		{"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
		{"label": "Fiscal Year", "fieldname": "fiscal_year", "fieldtype": "Link", "options": "Fiscal Year", "width": 150}
	]
	
	# Build conditions
	conditions = []
	values = []

	if filters.get("from_date"):
		conditions.append("je.posting_date >= %s")
		values.append(filters.get("from_date"))
		
		# Calculate annual period based on from_date
		annual_start_date = getdate(filters.get("from_date"))
		annual_end_date = add_years(annual_start_date, 1)
	else:
		annual_start_date = None
		annual_end_date = None

	if filters.get("to_date"):
		conditions.append("je.posting_date <= %s")
		values.append(filters.get("to_date"))

	if filters.get("company"):
		conditions.append("je.company = %s")
		values.append(filters.get("company"))

	if filters.get("fiscal_year"):
		conditions.append("je.fiscal_year = %s")
		values.append(filters.get("fiscal_year"))
		
		# Get fiscal year dates for annual calculation
		fiscal_year = frappe.get_value("Fiscal Year", filters.get("fiscal_year"), 
			["year_start_date", "year_end_date"], as_dict=1)
		if fiscal_year:
			annual_start_date = fiscal_year.year_start_date
			annual_end_date = fiscal_year.year_end_date

	if filters.get("account"):
		conditions.append("je.account = %s")
		values.append(filters.get("account"))

	# Strong filter for non-zero debit amounts
	conditions.append("COALESCE(je.debit_in_account_currency, 0) > 0")
	
	where_clause = " AND ".join(conditions) if conditions else "1=1"
	
	# Main query for period data
	query = f"""
		SELECT
			je.company,
			je.fiscal_year,
			je.cost_center,
			je.account,
			je.posting_date,
			SUM(CASE 
				WHEN acc.account_type LIKE 'Receivable%%' 
				THEN COALESCE(je.credit_in_account_currency, 0)
				ELSE 0 
			END) as receipt_amount,
			SUM(CASE 
				WHEN acc.account_type LIKE 'Payable%%' 
				THEN COALESCE(je.debit_in_account_currency, 0)
				ELSE 0 
			END) as payment_amount,
            SUM(CASE 
				WHEN acc.account_type LIKE 'Asset Received But Not Billed%%' 
				THEN COALESCE(je.debit_in_account_currency, 0)
				ELSE 0 
			END) as payment_amount
		FROM
			`tabGL Entry` je
		LEFT JOIN
			`tabAccount` acc
				ON acc.name = je.account
		WHERE {where_clause}
		GROUP BY
			je.company,
			je.fiscal_year,
			je.account
		ORDER BY
			je.posting_date DESC
	"""
	
	data = frappe.db.sql(query, tuple(values), as_dict=True)
	
	# Calculate annual totals
	annual_totals = {}
	for row in data:
		key = (row.get("company"), row.get("account"), row.get("cost_center"))
		
		if key not in annual_totals:
			annual_totals[key] = {
				"annual_receipt_amount": 0,
				"annual_payment_amount": 0
			}
		
		annual_totals[key]["annual_receipt_amount"] += row.get("receipt_amount", 0)
		annual_totals[key]["annual_payment_amount"] += row.get("payment_amount", 0)
	
	# Alternative: Query for annual totals directly from database
	if annual_start_date and annual_end_date:
		annual_conditions = []
		annual_values = []
		
		if filters.get("company"):
			annual_conditions.append("je.company = %s")
			annual_values.append(filters.get("company"))
		
		if filters.get("account"):
			annual_conditions.append("je.account = %s")
			annual_values.append(filters.get("account"))
		
		annual_conditions.append("je.posting_date >= %s")
		annual_values.append(annual_start_date)
		annual_conditions.append("je.posting_date <= %s")
		annual_values.append(annual_end_date)
		annual_conditions.append("COALESCE(je.debit_in_account_currency, 0) > 0")
		
		annual_where = " AND ".join(annual_conditions)
		
		annual_query = f"""
			SELECT
				je.company,
				je.account,
				je.cost_center,
				SUM(CASE 
					WHEN acc.account_type LIKE 'Receivable%%' 
					THEN COALESCE(je.credit_in_account_currency, 0)
					ELSE 0 
				END) as annual_receipt_amount,
				SUM(CASE 
					WHEN acc.account_type LIKE 'Payable%%' 
					THEN COALESCE(je.debit_in_account_currency, 0)
					ELSE 0 
				END) as annual_payment_amount
			FROM
				`tabGL Entry` je
			LEFT JOIN
				`tabAccount` acc
					ON acc.name = je.account
			WHERE {annual_where}
			GROUP BY
				je.company,
				je.account,
				je.cost_center
		"""
		
		annual_data = frappe.db.sql(annual_query, tuple(annual_values), as_dict=True)
		
		# Create a lookup dictionary for annual totals
		annual_lookup = {}
		for annual_row in annual_data:
			key = (annual_row.get("company"), annual_row.get("account"), annual_row.get("cost_center"))
			annual_lookup[key] = annual_row
	
	# Process and filter data
	result = []
	for row in data:
		# Skip if both receipt and payment amounts are zero
		if row.get("receipt_amount") == 0 and row.get("payment_amount") == 0:
			continue
		
		# Get annual amounts
		key = (row.get("company"), row.get("account"), row.get("cost_center"))
		
		if annual_start_date and annual_end_date and annual_lookup:
			annual_row = annual_lookup.get(key, {})
			row["annual_receipt_amount"] = annual_row.get("annual_receipt_amount", 0)
			row["annual_payment_amount"] = annual_row.get("annual_payment_amount", 0)
		else:
			# Use calculated annual totals from current data
			annual_total = annual_totals.get(key, {})
			row["annual_receipt_amount"] = annual_total.get("annual_receipt_amount", 0)
			row["annual_payment_amount"] = annual_total.get("annual_payment_amount", 0)
		
		row["total_amount"] = (row.get("receipt_amount") or 0) - (row.get("payment_amount") or 0)
		result.append(row)
	
	# Add summary row for totals
	if result:
		summary_row = {
			"account": "TOTAL",
			"receipt_amount": sum(row.get("receipt_amount", 0) for row in result),
			"payment_amount": sum(row.get("payment_amount", 0) for row in result),
			"annual_receipt_amount": sum(row.get("annual_receipt_amount", 0) for row in result),
			"annual_payment_amount": sum(row.get("annual_payment_amount", 0) for row in result),
			"total_amount": sum(row.get("total_amount", 0) for row in result),
			"idx": len(result) + 1
		}
		result.append(summary_row)
	
	# Add index numbers
	for idx, row in enumerate(result, start=1):
		if row.get("account") != "TOTAL":
			row["idx"] = idx

	return columns, result