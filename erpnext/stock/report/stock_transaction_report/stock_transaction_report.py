# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	if filters:
		data=get_datas(filters)
	else:
		data=[]
	columns= get_columns(filters)
	
	return columns, data

def get_columns(filters):
	columns= [
		{
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"label": _("Posting Date"),
			
		},
		{
			"fieldname": "item_code",
			"fieldtype": "Link",
			"label": _("Material Code"),
			"options": "Item",

		},
		{
			"fieldname": "item_name",
			"fieldtype": "Data",
			"label": _("Material Name"),
		},
		{
			"fieldname": "item_group",
			"fieldtype": "Data",
			"label": _("Material Sub Group"),
		},
		{
			"fieldname": "uom",
			"fieldtype": "Link",
			"label": _("UoM"),
			"options": "UOM",
		},
		{
			"fieldname": "qty",
			"fieldtype": "Float",
			"label": _("Dispatch Qty"),
		},
		{
			"fieldname": "valuation_rate",
			"fieldtype": "Currency",
			"label": _("Valuation Rate"),
		},
		{
			"fieldname": "amount",
			"fieldtype": "Currency",
			"label": _("Amount"),
		},
		{
			"fieldname": "name",
			# "fieldtype": "Data",
			"fieldtype": "Link",
			"options": "Stock Entry",
			
			"label": _("Stock Entry"),
		},
		{
			"fieldname": "s_warehouse",
			"fieldtype": "Link",
			"label": _("Source Warehouse"),
			"options": "Warehouse",
		},
		{
			"fieldname": "cost_center",
			"fieldtype": "Link",
			"label": _("Cost Center"),
			"options": "Cost Center",
		},
		{
			"fieldname": "issued_to_employee",
			"fieldtype": "Link",
			"label": _("Issued To"),
			"options": "Warehouse",
		},
		{
			"fieldname": "issue_to_employee_name",
			"fieldtype": "Link",
			"label": _("Issued Employee Name"),
			"options": "Employee",
		},
	
		{
			"fieldname": "expense_account",
			"fieldtype": "Link",
			"label": _("Expense Account"),
			"options": "Account",
		},]
	
	return columns

def get_conditions(filters):
	conditions=[]
	if filters.get("to_date"):
		conditions.append("st.posting_date <= '{}'".format(filters.get("to_date")))
	if filters.get("from_date"):
		conditions.append("st.posting_date >= '{}'".format(filters.get("from_date")))
	if filters.get("purpose"):
		conditions.append("st.purpose = '{}'".format(filters.get("purpose")))
	if filters.get("s_warehouse"):
		conditions.append("std.s_warehouse = '{}'".format(filters.get("s_warehouse")))
	if filters.get("t_warehouse"):
		conditions.append("std.t_warehouse = '{}'".format(filters.get("t_warehouse")))
	if filters.get("item_code"):
		conditions.append("std.item_code = '{}'".format(filters.get("item_code")))

	return " AND ".join(conditions)
	


def get_datas(filters):
	conditions=get_conditions(filters)
	conditions_clause = f"WHERE {conditions}" if conditions else ""

	stock_entry_data=frappe.db.get_all('Stock Entry', '*')
	stock_entry_detail_data=frappe.db.get_all('Stock Entry Detail','*')
	result=frappe.db.sql(
		f"""
			SELECT 
				st.name, st.posting_date, std.item_code, std.item_name,
				std.item_group, std.uom, std.qty, std.valuation_rate,
				std.amount, std.s_warehouse, std.cost_center,
				std.issue_to_employee, std.expense_account, std.issue_to_employee_name

			FROM 
				`tabStock Entry` st
			INNER JOIN 
				`tabStock Entry Detail` std ON st.name=std.parent
			{conditions_clause}
		"""
	, as_dict=True)

	

	
	return result