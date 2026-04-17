# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data

import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	filters = frappe._dict(filters or {})

	columns = get_columns()
	data = get_data(filters)

	# Calculate total_outstanding for each row
	for row in data:
		if row.get("opening_balance") and flt(row.get("opening_balance")) != 0:
			# If opening_balance exists, total_outstanding = opening_balance - advance_amount
			row["total_outstanding"] = flt(row.get("opening_balance")) + flt(row.get("advance_amount"))
		else:
			# If no opening_balance, total_outstanding = advance_amount
			row["total_outstanding"] = flt(row.get("advance_amount"))


	return columns, data


def get_columns():
	return [
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Data",
			"width": 180,
		},
		# {
		# 	"label": _("Parent Account"),
		# 	"fieldname": "broad_head",
		# 	"fieldtype": "Link",
		# 	"options": "Account",
		# 	"width": 180,
		# },
		# {
		# 	"label": _("Account"),
		# 	"fieldname": "account",
		# 	"fieldtype": "Link",
		# 	"options": "Account",
		# 	"width": 180,
		# },
		{
			"label": _("Advance Type"),
			"fieldname": "advance_type",
			"fieldtype": "Link",
			"width": 180,
			"options": "Advance Type",
		},
		{
			"label": _("Customer Name"),
			"fieldname": "customer",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"label": _("Customer ID"),
			"fieldname": "customer_cid",
			"fieldtype": "Data",
			"width": 180,
		},
		# {
		# 	"label": _("Employee"),
		# 	"fieldname": "employee",
		# 	"fieldtype": "Link",
		# 	"options": "Employee",
		# 	"width": 140,
		# },
		# {
		# 	"label": _("Employee Name"),
		# 	"fieldname": "employee_name",
		# 	"fieldtype": "Data",
		# 	"width": 180,
		# },
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Data",
			# "options": "Item",
			"width": 180,
		},
		# {
		# 	"label": _("Item Name"),
		# 	"fieldname": "item_name",
		# 	"fieldtype": "Data",
		# 	"width": 180,
		# },

		{
			"label": _("Activity Code"),
			"fieldname": "budget_activity",
			"fieldtype": "Link",
			"options": "Budget Activity",
			"width": 180,
		},
		{
			"label": _("FI code"),
			"fieldname": "account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 120,
		},
		{
			"label": _("Opening Balance"),
			"fieldname": "opening_balance",
			"fieldtype": "Currency",
			"width": 180,
		},
		{
			"label": _("FY Outstanding"),
			"fieldname": "advance_amount",
			"fieldtype": "Currency",
			"width": 180,
		},
		{
			"label": _("Total Outstanding"),
			"fieldname": "total_outstanding",
			"fieldtype": "Currency",
			"width": 180,
		},
		{
			"label": _("Remarks"),
			"fieldname": "remarks",
			"fieldtype": "Data",
			"width": 180,
		},
	]


def get_data(filters):
	conditions = []
	values = {}

	if filters.get("company"):
		conditions.append("a.company = %(company)s")
		values["company"] = filters.company

	if filters.get("advance_type"):
		conditions.append("a.advance_type = %(advance_type)s")
		values["advance_type"] = filters.advance_type	

	# if filters.get("employee"):
	# 	conditions.append("a.employee = %(employee)s")
	# 	values["employee"] = filters.employee

	if filters.get("customer"):
		conditions.append("a.customer = %(customer)s")
		values["customer"] = filters.customer

	if filters.get("from_date"):
		conditions.append("a.posting_date >= %(from_date)s")
		values["from_date"] = filters.from_date

	if filters.get("to_date"):
		conditions.append("a.posting_date <= %(to_date)s")
		values["to_date"] = filters.to_date

	if filters.get("docstatus") is not None and str(filters.get("docstatus")) != "":
		conditions.append("e.docstatus = %(docstatus)s")
		values["docstatus"] = int(filters.docstatus)

	where_clause = " AND ".join(conditions)
	if where_clause:
		where_clause = "WHERE " + where_clause

	data = frappe.db.sql(
		f"""
		SELECT
			a.posting_date,
			a.advance_type,
			a.customer_name,
			a.customer_cid,
			a.employee,
			a.employee_name,
			a.customer,
			a.posting_date,
			a.opening_balance,
			a.budget_activity,
			a.company,
			a.advance_amount,
			a.item_code,
			a.item_name,
			a.account
		FROM `tabAdvance` a
		{where_clause}
		ORDER BY a.posting_date DESC, a.name DESC
		""",
		values,
		as_dict=True,
	)

	return data
