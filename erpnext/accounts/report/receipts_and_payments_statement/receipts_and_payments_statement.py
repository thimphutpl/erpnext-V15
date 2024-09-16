# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe import _
import frappe
from frappe.utils import flt, getdate, formatdate, cstr, rounded, get_first_day, get_last_day
from erpnext.accounts.report.financial_statements_hms import filter_accounts, set_gl_entries_by_account, filter_out_zero_value_rows
from erpnext.accounts.accounts_custom_functions import get_child_cost_centers
from datetime import datetime, timedelta
from collections import OrderedDict

value_fields = ("opening_debit", "opening_credit", "debit", "credit", "mcredit", "mdebit", "closing_debit", "closing_credit")

def execute(filters=None):
	return _execute(filters)

def _execute(filters=None):
	if not filters:
		filters = {}
	validate_filters(filters)
	data    = get_data(filters)
	columns = get_columns()
	return columns, data

def validate_filters(filters):
	pass

def get_data(filters):
	accounts = frappe.db.sql("""
						  select name, parent_account, account_name, root_type, report_type, lft, rgt
						  from `tabAccount` where company=%s order by name asc 
						""", filters.company, as_dict=True)
	if not accounts:
		return None
	
	accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)
	min_lft, max_rgt = frappe.db.sql("""select min(lft), max(rgt) from 	`tabAccount` where company=%s""", (filters.company))[0]
	# frappe.throw(str(min_lft)+' '+str(str(max_rgt)))

	gl_entries_by_account = {}
	#Added below section of code to get correct opening and closing
	month_id = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}[filters.month]

	dates = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"], as_dict=False)
	start, end = [datetime.strptime(str(i), "%Y-%m-%d") for i in dates]
	year_start_date = frappe.db.get_value("Fiscal Year", filters.fiscal_year,["year_start_date"])
	months = OrderedDict(((start + timedelta(i)).strftime(r"%Y-%m"), None) for i in range((end - start).days)).keys()

	actual_date = [i for i in months if i[-2:] == month_id][0] + "-01"
	month_start = get_first_day(actual_date)
	month_end = get_last_day(actual_date)
	set_gl_entries_by_account(	
								filters.cost_center, 
								filters.business_activity,
								filters.company, 
								year_start_date, 
								month_end, 
								min_lft, 
								max_rgt,
								filters,
								gl_entries_by_account, 
								ignore_closing_entries=not flt(filters.with_period_closing_entry),
								ignore_opening_entries=False
							)

	# frappe.msgprint(str(gl_entries_by_account))

	opening_balances = get_opening_balances(filters, month_start, year_start_date)
	# frappe.throw("heklo"+str(opening_balances))

	total_row = calculate_values(accounts, gl_entries_by_account, opening_balances, filters, month_start, month_end)
	accumulate_values_into_parents(accounts, accounts_by_name)
	# frappe.throw(str(total_row))

	data = prepare_data(accounts, filters, total_row, parent_children_map)
	data = filter_out_zero_value_rows(data, parent_children_map,
		show_zero_values=filters.get("show_zero_values"))

	return data

def get_opening_balances(filters, month_start, year_start_date):
	balance_sheet_opening = get_rootwise_opening_balances(filters, "Balance Sheet", month_start, year_start_date)
	pl_opening = get_rootwise_opening_balances(filters, "Profit and Loss", month_start, year_start_date)
	# frappe.msgprint(str(pl_opening))

	balance_sheet_opening.update(pl_opening)
	# frappe.throw(str(balance_sheet_opening))
	return balance_sheet_opening

def get_rootwise_opening_balances(filters, report_type, month_start, year_start_date):
	if frappe.db.get_value("Ficsal Year", filters.fiscal_year, "is_calendar_year"):
		start_date = frappe.db.get_value("Ficsal Year", filters.fiscal_year, "year_start_date")
	else:
		if int(str(month_start).split('-')[1]) > 7:
			start_date = str(month_start).split('-')[0]+"-06-01"
		else:
			start_date = str(int(str(month_start).split('-')[0])-1)+"-06-01"
	additional_conditions = " and posting_date >= '{0}'".format(start_date) \
	if report_type == "Profit and Loss" else " "

	if not flt(filters.with_period_closing_entry):
		additional_conditions += " and ifnull(voucher_type, '')!='Period Closing Voucher'"
	
	#added business_activity filter
	if filters.business_activity:
		additional_conditions += " and business_activity = '{0}'".format(filters.business_activity)
	else:
		additional_conditions += " and 1 = 1 "
	
	if filters.cost_center:
		cost_centers = get_child_cost_centers(filters.cost_center)
		additional_conditions += " and cost_center IN %(cost_center)s"
	else:
		cost_centers = filters.cost_center
	# frappe.msgprint(str(additional_conditions))
	gle = frappe.db.sql("""
		select
			account, sum(debit) as opening_debit, sum(credit) as opening_credit
		from `tabGL Entry`
		where
			company=%(company)s
			{additional_conditions}
			and (posting_date < %(month_start)s or ifnull(is_opening, 'No') = 'Yes')
			and account in (select name from `tabAccount` where report_type=%(report_type)s and root_type != 'Liability')
			and against_voucher_type != 'Asset'
			group by account
		""".format(additional_conditions=additional_conditions),
		{
			"company": filters.company,
			"month_start": month_start,
			"report_type": report_type,
			"year_start_date": year_start_date,
			"cost_center": cost_centers
		},
		as_dict=True, debug = 0)
	
	opening = frappe._dict()
	for d in gle:
		# if d.account == '93.06-PWA: Suppliers-Mobilization Advances - GCC':
		# 	frappe.msgprint(str(d))
		# frappe.msgprint(str(d))
		opening.setdefault(d.account, d)
	return opening

def get_cost_centers_with_children(cost_centers):
	if not isinstance(cost_centers, list):
		cost_centers = [d.strip() for d in cost_centers.strip().split(",") if d]

	all_cost_centers = []
	for d in cost_centers:
		if frappe.db.exists("Cost Center", d):
			lft, rgt = frappe.db.get_value("Cost Center", d, ["lft", "rgt"])
			children = frappe.get_all("Cost Center", filters={"lft": [">=", lft], "rgt": ["<=", rgt]})
			all_cost_centers += [c.name for c in children]
		else:
			frappe.throw(_("Cost Center: {0} does not exist").format(d))

	return list(set(all_cost_centers))

def get_conditions(filters):
	conditions = []

	if filters.get("cost_center"):
		# filters.cost_center = get_cost_centers_with_children(filters.cost_center)
		conditions.append("cost_center in %(cost_center)s")

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def calculate_values(accounts, gl_entries_by_account, opening_balances, filters, month_start, month_end):
	init = {
		"opening_debit": 0.0,
		"opening_credit": 0.0,
		"mdebit" : 0.0,
		"debit": 0.0,
		"mcredit" : 0.0,
		"credit": 0.0,
		"closing_debit": 0.0,
		"closing_credit": 0.0
	}

	total_row = {
		"account": None,
		"account_name": _("Total"),
		"warn_if_negative": True,
		"opening_debit": 0.0,
		"opening_credit": 0.0,
		"mdebit" : 0.0,
		"debit": 0.0,
		"mcredit" : 0.0,
		"credit": 0.0,
		"closing_debit": 0.0,
		"closing_credit": 0.0
	}
	bank_closing_credit = bank_closing_debit = cash_closing_credit = cash_closing_debit = b_amount = c_amount = d_amount = 0

	for d in accounts:
		d.update(init.copy())

		# add opening
		d["opening_debit"] = opening_balances.get(d.name, {}).get("opening_debit", 0)
		d["opening_credit"] = opening_balances.get(d.name, {}).get("opening_credit", 0)
		# if d["name"] == '93.06-PWA: Suppliers-Mobilization Advances - GCC':
		# 	frappe.msgprint(str(d["opening_debit"]))
		opening = 0
		if d["account_name"] in ("12.B/80.02 - Bank Account - OGZ"):
			# frappe.msgprint(str(d))
			opening += d["opening_debit"] - d["opening_credit"]
			# frappe.msgprint(str(d["opening_credit"]))
			if opening > 0:
				d["opening_debit"] = opening
				d["opening_credit"] = 0
			else:
				d["opening_credit"] = opening
				d["opening_debit"] = 0
		a = b = c = e = 0

		for entry in gl_entries_by_account.get(d.name, []):
			if entry.account in ("12.B/80.02 - Bank Account - OGZ"):
				d["debit"] = 0
				d["credit"] = 0
				d["mdebit"] = 0
				d["mcredit"] = 0

			if cstr(entry.is_opening) != "Yes" and entry.account in ("12.B/80.02 - Bank Account - OGZ"):
					d["debit"] += flt(entry.debit, 3)
					d["credit"] += flt(entry.credit, 3)
				
			elif cstr(entry.is_opening) != "Yes":
				d["debit"] += flt(entry.debit, 3)
				d["credit"] += flt(entry.credit, 3)

			# if entry.posting_date >= month_start and entry.posting_date <= month_end and entry.account not in ("Bank & Cash Balances - GCC","12.a:Cash - GCC", "12.b:Bank - GCC", "80.02-CD AC 101214282 - GCC", "80.01-Cash in Hand - GCC"):
			if entry.posting_date >= month_start and entry.posting_date <= month_end:
				d["mdebit"] += flt(entry.debit, 3)
				d["mcredit"] += flt(entry.credit, 3)

			if entry.account in ("De-Suung fund AC 202944097 - DS"):
				bank_closing_credit += d["mcredit"]
				bank_closing_debit += d["mdebit"]
				# frappe.msgprint(str(bank_closing_debit)+" "+str(bank_closing_credit))

			if entry.account in ("Cash in Hand - DS"):
				cash_closing_credit = d["mcredit"]
				cash_closing_debit = d["mdebit"]
				# frappe.msgprint(str(cash_closing_debit)+" "+str(cash_closing_credit))
			
		# if d.name == "1.01-Pay & Allowances - GCC":
		# 	# frappe.msgprint(str(d["mdebit"])+" "+str(d["mcredit"]))
		# 	d["mdebit"] = d["mdebit"] - d["mcredit"]
		# 	d["mcredit"] = 0
		# 	d["debit"] = d["debit"] - d["credit"]
		# 	d["credit"] = 0
			
		# frappe.msgprint(str(d))
				# total_row["mdebit"] += d["opening_debit"]
		# frappe.msgprint("Here "+str(a)+" "+d.name+" "+str(d["credit"]))
		if d.name in ("De-Suung fund AC 202944097 - DS"):
			if a != 1:
				total_row["mcredit"] += d["opening_debit"] + d["opening_credit"]
				total_row["credit"] += d["opening_debit"] + d["opening_credit"] - d["credit"]
				a = 1


		if d.name in ("Cash in Hand - DS"):
			if b != 1:
				total_row["mcredit"] += d["opening_debit"] + d["opening_credit"]
				total_row["credit"] += d["credit"]
				b = 1

		# if d.name in ("80.02-CD AC 101214282 - GCC"):
		# 	if c != 1:
		# 		total_row["mdebit"] += d["closing_debit"]
		# 		total_row["debit"] += d["opening_debit"] - d["debit"]
		# 		# frappe.throw("Here "+str(d["credit"]))
		# 		c = 1


		# if d.name in ("80.01-Cash in Hand - GCC"):
		# 	if e != 1:
		# 		total_row["mdebit"] += d["closing_debit"]
		# 		total_row["debit"] += d["opening_debit"] - d["debit"]
		# 		e = 1
		# if d.name not in ('80.02-CD AC 101214282 - GCC','Bank & Cash Balances - GCC'):
		total_row["debit"] += d["debit"]
		total_row["mdebit"] += d["mdebit"]

		# frappe.msgprint(str(d["debit"]))
		if d.name not in ('12.B/80.02 - Bank Account - OGZ'):
			total_row["credit"] += d["credit"]
			total_row["mcredit"] += d["mcredit"]
	
	# total_row["debit"] += total_row["mdebit"]
	cb_closing_debit = cb_closing_credit = 0
	for d in accounts:
		if d["account_name"] in ('12.B/80.02 - Bank Account - OGZ'):
			b_amount = bank_closing_debit - bank_closing_credit + d["opening_debit"]
			# frappe.msgprint(str(bank_closing_credit)+" "+str(bank_closing_debit)+" "+str(d["opening_debit"]))	
			if b_amount > 0:
				d["closing_debit"] = b_amount
				cb_closing_debit += b_amount
			else:
				d["closing_credit"] = b_amount
				cb_closing_credit += b_amount
			# frappe.msgprint(str(b_amount))

		elif d["account_name"] in ("Cash in Hand"):
			c_amount = cash_closing_debit - cash_closing_credit + d["opening_debit"]
			# frappe.msgprint(str(cash_closing_credit)+" "+str(cash_closing_debit))
			if c_amount > 0:
				d["closing_debit"] = c_amount
				cb_closing_debit += c_amount
			else:
				d["closing_credit"] = c_amount
				cb_closing_credit += c_amount
		# else:
		# 	if d["name"] == "93.07-PWA: Suppliers-Secured Advances - GCC":
		# 		frappe.msgprint(str(d["opening_debit"]-d["mcredit"]+d["mdebit"]))
		# 	# frappe.msgprint(str(d["account_name"])+" "+str(d["opening_debit"]-d["mcredit"]+d["mdebit"]))
		# 	amount = d["opening_debit"] - d["mcredit"] + d["mdebit"]
		# 	if amount > 0:
		# 		d["closing_debit"] = amount
		# 	else:
		# 		d["closing_credit"] = amount
	for d in accounts:
		if d["account_name"] in ("12.B/80.02 - Bank Account - OGZ"):
				d["closing_debit"] = cb_closing_debit
				d["closing_credit"] = cb_closing_credit
		
		# for entry in gl_entries_by_account.get(d.name, []):
			# if cstr(entry.is_opening) == "Yes":
			# 	frappe.msgprint(str(entry.account))
			# frappe.msgprint(str(entry))

	# frappe.throw(str(bank_closing_credit)+" "+str(bank_closing_debit)+" cash "+str(cash_closing_credit)+" "+str(cash_closing_debit))
	return total_row

def accumulate_values_into_parents(accounts, accounts_by_name):
	for d in reversed(accounts):
		if d.parent_account:
			for key in value_fields:
				accounts_by_name[d.parent_account][key] += d[key]

def prepare_data(accounts, filters, total_row, parent_children_map):
	data = []
	for d in accounts:
		has_value = False
		if d.name not in ('Assets - OGZ'):
			row = {
				"account_name": d.account_name,
				"account": d.name,
				"parent_account": d.parent_account,
				"indent": d.indent,
				"from_date": filters.from_date,
				"to_date": filters.to_date
			}
		if d.name == 'Liabilities - OGZ':
			row = {
				"account_name": "Taxes",
				"account": d.name,
				"parent_account": d.parent_account,
				"indent": d.indent,
				"from_date": filters.from_date,
				"to_date": filters.to_date
			}
		if d.name == 'Bank & Cash - DS':
			row = {
				"account_name": "Bank & Cash",
				"account": d.name,
				"parent_account": "",
				"indent": 0,
				"from_date": filters.from_date,
				"to_date": filters.to_date
			}
		if d.name == 'Releases - OGZ':
			row = {
				"account_name": d.account_name,
				"account": d.name,
				"parent_account": "",
				"indent": 0,
				"from_date": filters.from_date,
				"to_date": filters.to_date
			}
		# if d.name == 'Receipts - DS':
		# 		row = {
		# 			"account_name": d.account_name,
		# 			"account": d.name,
		# 			"parent_account": d.parent_account,
		# 			"indent": d.indent,
		# 			"from_date": filters.from_date,
		# 			"to_date": filters.to_date
		# 		}
		if d.name not in ('Assets - OGZ'):
			prepare_opening_and_closing(d, total_row)
	
			for key in value_fields:
				row[key] = flt(d.get(key, 0.0), 3)
	
				if abs(row[key]) >= 0.005:
					# ignore zero values
					has_value = True
	
			row["has_value"] = has_value
			data.append(row)
	total_row["credit"] = total_row["credit"] - (total_row["credit"] - total_row["debit"])
	data.extend([{},total_row])

	return data

def prepare_opening_and_closing(d, total_row):
	# if d["account_name"] in ('b - Bank'):
	# 	#divided by 2 because the closing debit or credit for parent account is double somehow
	# 	if d["closing_debit"]:
	# 		d["closing_debit"] /= 2
	# 	else:
	# 		d["closing_credit"] /= 2
			
	if d["account_name"] in ('Bank & Cash'):
		#divided by 3 because the closing debit or credit for parent account is triple
		# frappe.throw(str(d["closing_debit"]))
		if d["closing_debit"]:
			d["closing_debit"] /= 2
		if d["closing_credit"]:
			d["closing_credit"]	/= 2
	# if d["name"] == "93.06-PWA: Suppliers-Mobilization Advances - GCC":
	# 	frappe.msgprint(str(d["opening_credit"]))

	if d["account_name"] not in ("De-Suung fund AC 202944097","a - Cash","Cash in Hand","b - Bank", "Bank & Cash"):
		if d["opening_debit"] > d["opening_credit"]:
			# if d["name"] == "93.06-PWA: Suppliers-Mobilization Advances - GCC":
			# 	frappe.msgprint(str(d["opening_debit"]-d["opening_credit"]))
			d["opening_debit"] -= d["opening_credit"]
			d["opening_credit"] = 0.0

		else:
			d["opening_credit"] -= d["opening_debit"]
			d["opening_debit"] = 0.0


		d["closing_debit"] = d["opening_debit"] - d["mcredit"] + d["mdebit"]
		d["closing_credit"] = d["opening_credit"] - d["mdebit"] + d["mcredit"]
		# frappe.msgprint("for account "+str(d["name"])+" "+str(d["closing_credit"])+" = "+str(d["opening_debit"])+"+"+str(d["mdebit"])+"-"+str(d["mcredit"]))
		if d["closing_debit"] > d["closing_credit"]:
			# d["closing_debit"] -= d["closing_credit"]
			d["closing_credit"] = 0.0

		else:
			# d["closing_credit"] -= d["closing_debit"]
			d["closing_debit"] = 0.0
	
	if d.name in ("De-Suung fund AC 202944097 - DS", "Cash in Hand - DS"):
		# if c != 1:
		# frappe.msgprint(str(total_row["debit"])+" "+str(d["closing_debit"])+" "+str(d["debit"]))
		total_row["mdebit"] += d["closing_debit"] + d["closing_credit"]
		total_row["debit"] += d["closing_debit"] + d["closing_credit"] - d["debit"]

	# Added below code to remove the mid section figures for cash and bank accounts in the report // Kinley Dorji 2021/02/03
	if d["name"] in ("Bank & Cash - DS", "De-Suung fund AC 202944097 - DS", "b - Bank - DS"):
		d["debit"] = 0
		d["credit"] = 0
		d["mdebit"] = 0
		d["mcredit"] = 0

	if d["name"] in ("a - Cash - DS", "Cash in Hand - DS"):
		d["debit"] = 0
		d["mdebit"] = 0

	# if d["name"] == "1.01-Pay & Allowances - GCC":
	# 	d["credit"] = 0
	# 	d["mcredit"] = 0
								
	if str(d.account_name.encode('utf-8')) in ["Assets", "Liabilities", "Equity", "Revenue", "Expenses"]:
		total_row['opening_credit'] = total_row['opening_credit'] + d['opening_credit']
		total_row['opening_debit'] = total_row['opening_debit'] + d['opening_debit']
		total_row['closing_credit'] = total_row['closing_credit'] + d['closing_credit']
		total_row['closing_debit'] = total_row['closing_debit'] + d['closing_debit']

def get_columns():
	return [
		{
			"fieldname": "account",
			"label": _("Group/Broad Head Of Account"),
			"fieldtype": "Link",
			"options": "Account",
			"width": 300
		},
		#	{
		#		"fieldname": "account_code",
		#		"label": _("Account Code"),
		#		"fieldtype": "Data",
		#		"width": 100
		#	},
		{
			"fieldname": "opening_debit",
			"label": _("Opening (Dr)"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "opening_credit",
			"label": _("Opening (Cr)"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "mdebit",
			"label": _("Receipts For The Month"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "debit",
			"label": _("Annual Progressive Debit"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "mcredit",
			"label": _("Payments For the Month"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "credit",
			"label": _("Annual Progressive Credit"),
			"fieldtype": "Currency",
			"width": 150
		},
		#	{
		#		"fieldname": "mcredit",
		#       "label": _("For the Month Credit"),
		#       "fieldtype": "Currency",
		#       "width": 150
		#   },

		#	{
		#		"fieldname": "credit",
		#		"label": _("Annual Progressive Credit"),
		#		"fieldtype": "Currency",
		#		"width": 150
		#	},
		{
			"fieldname": "closing_debit",
			"label": _("Closing (Dr)"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "closing_credit",
			"label": _("Closing (Cr)"),
			"fieldtype": "Currency",
			"width": 150
		}
	]