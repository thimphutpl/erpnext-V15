# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_data(filters=None):
	data = []
	cond = ''
	if filters.project_definition:
		cond += " and project_definition = %s" % frappe.db.escape(filters.project_definition)
	project_data = frappe.db.sql("""select name, cost_center, project_definition 
		from `tabProject` 
		where docstatus != 2 
		{cond}
	""".format(cond=cond),as_dict=True)

	for raw in project_data:
		total_debit, total_credit = 0, 0
		gl_cond = "and gl.account = %s" if filters.account else ""

		overall_expense = frappe.db.sql(
			"""select sum(gl.debit) as expense, sum(gl.credit) as income 
				from `tabGL Entry` gl
				inner join `tabAccount` acc on acc.name = gl.account
				where is_cancelled = 0
				and acc.root_type = 'Expense'
				and posting_date between %s and %s
				and project = %s
				{cond}""".format(cond=gl_cond),
			(filters.from_date, filters.to_date, raw.name, filters.account) if filters.account else (filters.from_date, filters.to_date, raw.name),
			as_dict=True
		)

		if overall_expense:
			total_debit = overall_expense[0].get("expense", 0)
			total_credit = overall_expense[0].get("income", 0)

		difference = flt(total_debit) - flt(total_credit)

		row = frappe._dict({
			"cost_center": raw.cost_center,
			"project": raw.name,
			"expense": total_debit,
			"income": total_credit,
			"total_expense": difference,
			"from_date": filters.from_date,
			"to_date": filters.to_date
		})
		data.append(row)

	return data

def build_condition(filters):
	 cond = ""
	 if filters.project_definition:
		  cond += "and project_definition = %s"
	 return cond

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
			"fieldname":"project",
			"fieldtype":"Link",
			"width":250,
			"label":"Project",
			"options":"Project"
		},
		{
			"fieldname":"expense",
			"fieldtype":"Data",
			"width":150,
			"label":"Expense"
		},
		{
			"fieldname":"income",
			"fieldtype":"Data",
			"width":150,
			"label":"Income"
		},
		{
			"fieldname":"total_expense",
			"fieldtype":"Data",
			"width":150,
			"label":"Total Expense"
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
		}
	]


