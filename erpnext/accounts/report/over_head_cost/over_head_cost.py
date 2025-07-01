# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_data(filters=None):
	data = []
	query = "select sum(gl.debit) as debit, sum(gl.credit) as credit from `tabGL Entry` gl inner join `tabAccount` ac on ac.name=gl.account where gl.is_cancelled = 0 and ac.root_type ='Expense' and gl.project in('','Null')"
	
	if filters.from_date and filters.to_date:
		query += " and gl.posting_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"
	
	if filters.cost_center:
		if filters.cost_center in [
			"Gyalpozhing - GYALSUNG", "Head Office - GYALSUNG", "Jamtsholing - GYALSUNG",
			"Khotokha - GYALSUNG", "Pemathang - GYALSUNG", "Tareythang - GYALSUNG"
		]:
			data = frappe.db.get_all(
				"Cost Center",
				filters={"parent_cost_center": filters.cost_center},
				fields=["name"]
			)
			child_cost_center = [d['name'] for d in data]
			if child_cost_center:
				placeholders = ", ".join(f"'{cc}'" for cc in child_cost_center)
				query += f" and gl.cost_center in ({placeholders})"
		else:
			query += f" and gl.cost_center = '{filters.cost_center}'"

	for raw in frappe.db.sql(query, as_dict=True):
		if not raw.debit or not raw.credit:
			over_head_cost = 0
		else:
			over_head_cost=raw.debit - raw.credit
			
		if not filters.cost_center:
			filters.cost_center = "GYALSUNG INFRA - GYALSUNG"
		row = frappe._dict({ 
			"cost_center":filters.cost_center, 
			"from_date":filters.from_date, 
			"to_date":filters.to_date, 
			"total_expense":raw.debit, 
			"total_income":raw.credit, 
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
			"fieldname":"over_head_cost",
			"fieldtype":"Data",
			"width":150,
			"label":"Over Head Cost"
		},
	]

