# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from collections import OrderedDict
from datetime import datetime, timedelta

import frappe
from frappe import _
from frappe.utils import add_days, cstr, flt, formatdate, get_first_day, get_last_day, getdate, rounded


def execute(filters=None):
	return _execute(filters)

def _execute(filters=None):
	filters = filters or {}
	validate_filters(filters)
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def validate_filters(filters):
	if not filters.fiscal_year:
		frappe.throw(_("Fiscal Year for {0} is required").format(filters.company))

def get_conditions(filters):
	conditions = ""
	conditions1 = ""
	if filters.get('cost_center'):
		conditions += " and cost_center = %(cost_center)s"
		conditions1 += " and t1.cost_center = %(cost_center)s"
	if filters.get('business_activity'):
		conditions += " and business_activity = %(business_activity)s"
		conditions1 += " and t2.business_activity = %(business_activity)s"
	return conditions, conditions1

def get_business_activity_code(cc, ba):
	query = """
		SELECT code
		FROM `tabSub Activity`
		WHERE parent = %(cc)s
		AND business_activity = %(ba)s
	"""
	result = frappe.db.sql(query, {'cc': cc, 'ba': ba}, as_dict=True)
	return result[0]['code'] if result else None

def get_budget_code(account):
	code = frappe.db.get_value("Budget Type", frappe.db.get_value("Account", account, 'budget_type'), "budget_code")
	return code if code else None

def get_data(filters):
	accounts = frappe.db.sql("""
						  select name, parent_account, account_name, root_type, report_type, lft, rgt
						  from `tabAccount` where company=%s and ledger in ("Opex", "Capex") order by name asc
						""", filters.company, as_dict=True)
	if not accounts:
		return None

	"""Fetch GL entries and structure them with headers and subheaders."""
	data = []

	month_id = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}[filters.month]

	dates = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"], as_dict=False)

	start, end = (datetime.strptime(str(i), "%Y-%m-%d") for i in dates)
	year_start_date = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ["year_start_date"])

	months = OrderedDict(((start + timedelta(i)).strftime(r"%Y-%m"), None) for i in range((end - start).days)).keys()

	actual_date = next(i for i in months if i[-2:] == month_id) + "-01"
	month_start = get_first_day(actual_date)
	month_end = get_last_day(actual_date)

	# Fetch GL entries
	conditions, conditions1 = get_conditions(filters)
	query = f"""
 				select
	 				account, debit, cost_center, business_activity, posting_date
				from `tabGL Entry`
				where docstatus = 1
				and is_cancelled = 0
				and company = %(company)s
				{conditions}
				and posting_date >= %(start_date)s and posting_date <= %(month_end)s
				order by cost_center ASC
			"""

	# Fetch from Purchase Invoice
	query1 = f"""select
 					t1.cost_center, t2.amount as debit, t2.business_activity, t2.sub_ledger as account, t1.posting_date
				from
					`tabPurchase Invoice` t1, `tabPurchase Invoice Item` t2
				where
					t1.name = t2.parent
					and t1.docstatus = 1
					and t1.payment_status = "Paid"
					and t1.posting_date >= %(start_date)s and posting_date <= %(month_end)s
					and t1.company = %(company)s
					{conditions1}
				order by t1.cost_center
			"""

	gl_entries = frappe.db.sql(query, {
		**filters,
		'start_date': year_start_date,
		'month_end': month_end
	}, as_dict=True) + frappe.db.sql(query1, {
		**filters,
		'start_date': year_start_date,
		'month_end': month_end
	}, as_dict=True)

	filtered_accounts = get_account_filtered_capex_opex(gl_entries)
	data = prepare_data(accounts, filtered_accounts, filters, year_start_date, month_start, month_end)
	return data

def prepare_data(accounts, filtered_accounts, filters, year_start_date, month_start, month_end):
	row_data = []

	# Dictionary to accumulate grouped data (Account, Cost Center, Business Activity)
	grouped_data = {}

	for d in filtered_accounts:
		# Generate the unique key for grouping by Account, Cost Center, and Business Activity
		group_key = (d['account'], d['cost_center'], d['business_activity'])

		# Get Cost Center Code, Business Activity Code, and Budget Code
		cc_code = frappe.db.get_value("Cost Center", d['cost_center'], 'cost_center_number')
		ba_code = get_business_activity_code(d['cost_center'], d['business_activity'])
		fg_code = get_budget_code(d['account'])
		obj_code = frappe.db.get_value("Account", d['account'], 'account_number')

		# Expenditure for the month
		expenditure = d['debit']

		# Initialize the group if not already present in grouped_data
		if group_key not in grouped_data:
			grouped_data[group_key] = {
				'cc_code': cc_code,
				'ba_code': ba_code,
				'fg_code': fg_code,
				'obj_code': obj_code,
				'account_name': d['account'],
				'monthly_expenditure': 0.0,
				'annual_expenditure': 0.0
			}

		# Add the monthly expenditure to the group's total for this month
		if month_start <= d.posting_date <= month_end:
			grouped_data[group_key]['monthly_expenditure'] += expenditure

		# Add to the annual expenditure (sum of all debits from the fiscal year to the current date)
		if year_start_date <= d.posting_date <= month_end:
			grouped_data[group_key]['annual_expenditure'] += expenditure

	# Convert the grouped data dictionary to a list of rows for the report
	for key, value in grouped_data.items():
		row_data.append({
			'ac_code': value['cc_code'],
			'ba_code': value['ba_code'],
			'fg_code': value['fg_code'],
			'obc': value['obj_code'],
			'account_name': value['account_name'],
			'monthly_expenditure': value['monthly_expenditure'],
			'annual_expenditure': value['annual_expenditure'],
		})

	return row_data

def get_total_debit_previous_month(accounts, account, year_start_date, month_start):
	total = 0
	previous_month_end = add_days(month_start, -1)
	previous_month_start = year_start_date
	for d in accounts:
		if d['account'] == account and previous_month_start <= d['posting_date'] <= previous_month_end:
			total += d['debit']
	return total

def get_account_filtered_capex_opex(gl_entries):
	filtered_data = []
	for entry in gl_entries:
		account_type = get_account_type(entry['account'])
		if account_type:
			filtered_data.append(entry)
	return filtered_data

def get_account_type(account):
	"""Determine the account type (Opex or Capex) based on the ledger type."""
	ledger_type = frappe.db.get_value("Account", {"name": account}, "ledger")
	return ledger_type if ledger_type in ["Opex", "Capex"] else ""

def get_columns(filters):
	"""Define the structure and labels for report columns."""
	return [
		{"label": _("AC"), "fieldname": "ac_code", "fieldtype": "Data"},
		{"label": _("SAC"), "fieldname": "ba_code", "fieldtype": "Data"},
		{"label": _("FIC"), "fieldname": "fg_code", "fieldtype": "Data"},
		{"label": _("OBC"), "fieldname": "obc", "fieldtype": "Data"},
		{"label": _("Account"), "fieldname": "account_name", "fieldtype": "Link", "options": "Account"},
		{"label": _("Expenditure for the Month (Nu.)"), "fieldname": "monthly_expenditure", "fieldtype": "Float"},
		{"label": _("Annual Progressive Expenditure (Nu.)"), "fieldname": "annual_expenditure", "fieldtype": "Float"},
	]
