# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
def execute(filters=None):
	columns  = get_columns()
	data = get_data(filters or {})
	return columns, data

def get_columns():
	return [
		{
			"fieldname": "equipment_number",
			"label": "Equipment Number",
			"fieldtype": "Data",
			"options": "Equipment Number",
			"width": 150,
		},
	]
def get_data(filters):
	query = """
			select jc.equipment_number from `tabJob Cards` As jc  WHERE jc.docstatus = 1
		"""
	if filters.get("cost_center"):
		query += " and jc.cost_center = \'" + str(filters.cost_center) + "\'"
	if filters.get("from_date") and filters.get("to_date"):
		query += " and jc.posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	return frappe.db.sql(query)