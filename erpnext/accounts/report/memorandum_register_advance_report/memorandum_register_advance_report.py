# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe

# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


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
	
	# Add date range filters if provided
	if filters.get("from_date"):
		conditions.append("gl.posting_date >= %(from_date)s")
	
	if filters.get("to_date"):
		conditions.append("gl.posting_date <= %(to_date)s")
	
	# Add voucher type filter if provided
	if filters.get("voucher_type"):
		conditions.append("gl.voucher_type = %(voucher_type)s")
	
	# Add voucher no filter if provided
	if filters.get("voucher_no"):
		conditions.append("gl.voucher_no = %(voucher_no)s")
	
	# Add account filter if provided
	if filters.get("account"):
		conditions.append("gl.account = %(account)s")

	# Add account filter if provided
	if filters.get("broad_head"):
		conditions.append("jea.broad_head = %(broad_head)s")	

	# Add group account filter - show only group accounts
	if filters.get("group_account"):
		conditions.append("acc.is_group = 1")	

	# Add company filter if provided
	if filters.get("company"):
		conditions.append("gl.company = %(company)s")

	# Add budget activity filter if provided
	if filters.get("budget_activity"):
		conditions.append("gl.budget_activity = %(budget_activity)s")	

	# Add party filter if provided
	if filters.get("party"):
		conditions.append("gl.party = %(party)s")		

	return " AND {}".format(" AND ".join(conditions)) if conditions else ""

def get_gl_entries(filters):
	conditions = get_conditions(filters)
	
	gl_entries = frappe.db.sql(
		f"""
		SELECT
			gl.name as gl_entry, 
			gl.posting_date, 
			gl.account, 
			acc.is_group,
			acc.parent_account,
			gl.party_type, 
			gl.party,
			gl.voucher_type, 
			gl.voucher_subtype, 
			gl.voucher_no,
			gl.cost_center, 
			gl.project,
			gl.against_voucher_type, 
			gl.against_voucher, 
			gl.account_currency,
			gl.against, 
			gl.is_opening, 
			gl.creation, 
			gl.credit, 
			gl.debit,
			gl.company,
			jea.broad_head,
			jea.budget_activity,
			jea.budget_sub_activity
		FROM `tabGL Entry` gl
		INNER JOIN `tabJournal Entry Account` jea 
			ON jea.parent = gl.voucher_no 
			AND jea.account = gl.account
		INNER JOIN `tabAccount` acc 
			ON acc.name = gl.account
		WHERE gl.is_cancelled = 0 
			AND gl.voucher_type = 'Journal Entry'
			{conditions}
		ORDER BY gl.posting_date DESC, gl.creation DESC
	""",
		filters,
		as_dict=1,
	)
	
	return gl_entries

def get_columns(filters):
	columns = [
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
		{
			"label": _("Parent Account"),
			"fieldname": "broad_head",
			"fieldtype": "Link",
			"options": "Account",
			"width": 180,
		},
		{
			"label": _("Account"),
			"fieldname": "account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 180,
		},
		{
			"label": _("Budget Activity"),
			"fieldname": "budget_activity",
			"fieldtype": "Link",
			"options": "Budget Activity",
			"width": 180,
		},
		{
			"label": _("Budget Sub Activity"),
			"fieldname": "budget_sub_activity",
			"fieldtype": "Link",
			"options": "Budget Sub Activity",
			"width": 180,
		},
		# {
		# 	"label": _("Is Group Account"),
		# 	"fieldname": "is_group",
		# 	"fieldtype": "Check",
		# 	"width": 120,
		# },
		# {
		# 	"label": _("Parent Account"),
		# 	"fieldname": "parent_account",
		# 	"fieldtype": "Link",
		# 	"options": "Account",
		# 	"width": 180,
		# },
		# {"label": _("Account Type"), "fieldname": "account_type", "fieldtype": "Data", "width": 120},
		{"label": _("Cost Center"), "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 180},
		{"label": _("Voucher Type"), "fieldname": "voucher_type", "width": 120},
		{
			"label": _("Voucher No"),
			"fieldname": "voucher_no",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 180,
		},
		{"label": _("Credit Amount"), "fieldname": "credit", "fieldtype": "Currency", "width": 120},
		{"label": _("Debit Amount"), "fieldname": "debit", "fieldtype": "Currency", "width": 120},
		{"label": _("Against Account"), "fieldname": "against", "width": 150},
		{"label": _("Party Type"), "fieldname": "party_type", "width": 100},
		{"label": _("Party"), "fieldname": "party", "width": 150},
		{"label": _("Company"), "fieldname": "company", "width": 150},
	]

	return columns