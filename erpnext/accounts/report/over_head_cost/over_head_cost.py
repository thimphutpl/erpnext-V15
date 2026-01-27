# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_data(filters=None):
	data = []
	query = "select sum(gl.debit) as debit, sum(gl.credit) as credit from `tabGL Entry` gl inner join `tabAccount` ac on ac.name=gl.account where gl.is_cancelled = 0 and ac.root_type ='Expense' and (gl.project IS NULL OR gl.project = '')"
	
	if filters.from_date and filters.to_date:
		query += " and gl.posting_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"
		cond = " and gl.posting_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"
	if filters.cost_center:
		if filters.cost_center in [
			"Gyalpozhing - GYALSUNG", "Head Office - GYALSUNG", "Jamtsholing - GYALSUNG",
			"Khotokha - GYALSUNG", "Pemathang - GYALSUNG", "Tareythang - GYALSUNG"
		]:
			child_data = frappe.db.get_all(
				"Cost Center",
				filters={"parent_cost_center": filters.cost_center},
				fields=["name"]
			)
			child_cost_center = [d['name'] for d in child_data]
			if child_cost_center:
				placeholders = ", ".join(f"'{cc}'" for cc in child_cost_center)
				query += f" and gl.cost_center in ({placeholders})"
				cond = f" and gl.cost_center in ({placeholders})"
		else:
			query += f" and gl.cost_center = '{filters.cost_center}'"
			cond = f" and gl.cost_center = '{filters.cost_center}'"
	if filters.account:
		query += f" and gl.account = '{filters.account}'"
		cond += f" and gl.account = '{filters.account}'"
	over_head_data = frappe.db.sql(query, as_dict=True)
	overall_expense = frappe.db.sql(""" select sum(gl.debit) as expense, sum(gl.credit) as income 
		from `tabGL Entry` gl
		inner join `tabAccount` ac 
		on ac.name=gl.account
		and gl.is_cancelled = 0
		and ac.root_type='Expense'
		{cond}
	""".format(cond=cond),as_dict=True)
	expense = income = 0

	for x in overall_expense:
		expense = x.expense if x.expense else 0
		income = x.income if x.income else 0

	for raw in over_head_data:
		if not filters.cost_center:
			filters.cost_center = "GYALSUNG INFRA - GYALSUNG"
		total_debit = raw.debit if raw.debit else 0
		total_credit = raw.credit if raw.credit else 0
		over_head_cost =total_debit-total_credit

		row = frappe._dict({ 
			"cost_center":filters.cost_center, 
			"from_date":filters.from_date, 
			"to_date":filters.to_date, 
			"total_expense": expense, 
			"total_income": income, 
			"total_over_headexpense": total_debit,
			"total_over_head_income": total_credit,
			"over_head_cost": over_head_cost if over_head_cost > 0 else 0
		})
		data.append(row)
	return data

def get_columns():
	return [
		{	
			"fieldname":"cost_center",
			"fieldtype":"Link",
			"width":250,
			"label":"Cost Center",
			"options":"Cost Center"
		},
		{
			"fieldname":"from_date",
			"fieldtype":"Date",
			"width":120,
			"label":"From Date"
		},
		{
			"fieldname":"to_date",
			"fieldtype":"Date",
			"width":120,
			"label":"To Date"
		},
		{
			"fieldname":"total_expense",
			"fieldtype":"Data",
			"width":150,
			"label":"Total Expense"
		},
		{
			"fieldname":"total_income",
			"fieldtype":"Data",
			"width":150,
			"label":"Total Income"
		},
		{
			"fieldname":"total_over_headexpense",
			"fieldtype":"Data",
			"width":200,
			"label":"Total Overhead Expense"
		},
		{
			"fieldname":"total_over_head_income",
			"fieldtype":"Data",
			"width":200,
			"label":"Total Overhead Income"
		},
		{
			"fieldname":"over_head_cost",
			"fieldtype":"Data",
			"width":150,
			"label":"Over Head Cost"
		},
	]

