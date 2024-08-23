# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe import _
import frappe


def execute(filters=None):
	return _execute(filters)

def _execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns(filters)
	data    = get_data(filters)
	return columns, data

def get_data(filters):
	gl_entries = get_gl_entries(filters)
	return gl_entries

def get_conditions(filters):
	conditions = []

	# if filters.get("cost_center"):
	# 	filters.cost_center = get_cost_centers_with_children(filters.cost_center)
	# 	conditions.append("cost_center in %(cost_center)s")

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def get_gl_entries(filters):
	gl_entries = frappe.db.sql(
		f"""
		select
			name as gl_entry, posting_date, account, party_type, party,
			voucher_type, voucher_subtype, voucher_no,
			cost_center, project,
			against_voucher_type, against_voucher, account_currency,
			against, is_opening, creation
		from `tabGL Entry`
		where is_cancelled = 0 {get_conditions(filters)}
	""",
		filters,
		as_dict=1,
	)
	return gl_entries

def get_columns(filters):
	columns = [
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
		{
			"label": _("Account"),
			"fieldname": "account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 180,
		},
		{"label": _("Cost Center"), "fieldname": "cost_center", "width": 180},
		{"label": _("Voucher Type"), "fieldname": "voucher_type", "width": 120},
		{
			"label": _("Voucher No"),
			"fieldname": "voucher_no",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 180,
		},
		{"label": _("Against Account"), "fieldname": "against", "width": 150},
		{"label": _("Party Type"), "fieldname": "party_type", "width": 100},
		{"label": _("Party"), "fieldname": "party", "width": 150},
	]

	return columns
