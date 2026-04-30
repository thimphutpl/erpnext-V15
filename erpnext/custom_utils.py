from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe import msgprint
from frappe.utils import flt, cint, nowdate, getdate, formatdate
from erpnext.accounts.utils import get_fiscal_year
from frappe.utils.data import get_first_day, get_last_day, add_years
from frappe.desk.form.linked_with import get_linked_doctypes, get_linked_docs
from frappe.model.naming import getseries

#function to get the difference between two dates
@frappe.whitelist()
def get_date_diff(start_date, end_date):
	if start_date is None:
		return 0
	elif end_date is None:
		return 0
	else:
		return frappe.utils.data.date_diff(end_date, start_date) + 1

##
# Check for future dates in transactions
##
def check_future_date(date):
	if not date:
		frappe.throw("Date Argument Missing")
	if getdate(date) > getdate(nowdate()):
		frappe.throw("Posting for Future Date is not Permitted")

##
# Get cost center from branch
##
def get_branch_cc(branch):
	if not branch:
		frappe.throw("No Branch Argument Found")
	doc = frappe.get_doc("Branch", branch)
	return doc.cost_center

##
# Rounds to the nearest 5 with precision of 1 by default
##
def round5(x, prec=1, base=0.5):
	return round(base * round(flt(x)/base), prec)

##
# If the document is linked and the linked docstatus is 0 and 1, return the first linked document
##
def check_uncancelled_linked_doc(doctype, docname):
	linked_doctypes = get_linked_doctypes(doctype)
	linked_docs = get_linked_docs(doctype, docname, linked_doctypes)
	for docs in linked_docs:
		for doc in linked_docs[docs]:
			if doc['docstatus'] < 2:
				frappe.throw("There is an uncancelled " + str(frappe.get_desk_link(docs, doc['name']))+ " linked with this document")

def get_year_start_date(date):
	return str(date)[0:4] + "-01-01"

def get_year_end_date(date):
	return str(date)[0:4] + "-12-31"

# Ver 2.0 Begins, following method added by SHIV on 28/11/2017
@frappe.whitelist()
def get_user_info(user=None, employee=None, cost_center=None, branch=None):
	info = {}
	
	#cost_center,branch = frappe.db.get_value("Employee", {"user_id": user}, ["cost_center", "branch"])

	if employee:
		# Nornal Employee
		cost_center = frappe.db.get_value("Employee", {"name": employee}, "cost_center")
		branch      = frappe.db.get_value("Employee", {"name": employee}, "branch")

		# DES Employee
		if not cost_center:
			cost_center = frappe.db.get_value("DES Employee", {"name": employee}, "cost_center")
			branch      = frappe.db.get_value("DES Employee", {"name": employee}, "branch")

		# MR Employee
		if not cost_center:
			cost_center = frappe.db.get_value("Muster Roll Employee", {"name": employee}, "cost_center")
			branch      = frappe.db.get_value("Muster Roll Employee", {"name": employee}, "branch")
		
	elif user:
		# Normal Employee
		cost_center = frappe.db.get_value("Employee", {"user_id": user}, "cost_center")
		branch      = frappe.db.get_value("Employee", {"user_id": user}, "branch")

		# DES Employee
		if not cost_center:
			cost_center = frappe.db.get_value("DES Employee", {"user_id": user}, "cost_center")
			branch      = frappe.db.get_value("DES Employee", {"user_id": user}, "branch")

		# MR Employee
		# if not cost_center:
		# 	cost_center = frappe.db.get_value("Muster Roll Employee", {"user_id": user}, "cost_center")
		# 	branch      = frappe.db.get_value("Muster Roll Employee", {"user_id": user}, "branch")

	elif branch:
		cost_center = frappe.db.get_value("Branch", branch, "cost_center")
		# branch      = frappe.db.get_value("Employee", {"user_id": user}, "branch")

		# GEP Employee
		if not cost_center:
			cost_center = frappe.db.get_value("GEP Employee", {"user_id": user}, "cost_center")
			branch      = frappe.db.get_value("GEP Employee", {"user_id": user}, "branch")

		# MR Employee
		if not cost_center:
			cost_center = frappe.db.get_value("Muster Roll Employee", {"user_id": user}, "cost_center")
			branch      = frappe.db.get_value("Muster Roll Employee", {"user_id": user}, "branch")
		
	warehouse   = frappe.db.get_value("Cost Center", cost_center, "warehouse")
	approver    = frappe.db.get_value("Approver Item", {"cost_center": cost_center}, "approver")
	# customer    = frappe.db.get_value("Customer", {"cost_center": cost_center}, "name")

	info.setdefault('cost_center', cost_center)
	info.setdefault('branch', branch)
	info.setdefault('warehouse', warehouse)
	info.setdefault('approver',approver)
	# info.setdefault('customer', customer)
	
	#return [cc, wh, app, cust]
	return info
# Ver 2.0 Ends

##
#  nvl() function added by SHIV on 02/02/2018
##
def nvl(val1, val2):
	return val1 if val1 else val2

##
# generate and get the receipt number
##
def generate_receipt_no(doctype, docname, branch, fiscal_year):
	if doctype and docname:
		abbr = frappe.db.get_value("Branch", branch, "abbr")
		if not abbr:
			frappe.throw("Set Branch Abbreviation in Branch Master Record")
		name = str("NRDCL/" + str(abbr) + "/" + str(fiscal_year) + "/")
		current = getseries(name, 4)
		doc = frappe.get_doc(doctype, docname)
		doc.db_set("money_receipt_no", current)
		doc.db_set("money_receipt_prefix", name)

##
#  get_prev_doc() function added by SHIV on 03/22/2018
##
@frappe.whitelist()
def get_prev_doc(doctype,docname,col_list=""):
	if col_list:
		return frappe.db.get_value(doctype,docname,col_list.split(","),as_dict=1)
	else:
		return frappe.get_doc(doctype,docname)

##
# Prepre the basic stock ledger 
##
def prepare_sl(d, args):
	sl_dict = frappe._dict({
		"item_code": d.pol_type,
		"warehouse": d.warehouse,
		"posting_date": d.posting_date,
		"posting_time": d.posting_time,
		'fiscal_year': get_fiscal_year(d.posting_date, company=d.company)[0],
		"voucher_type": d.doctype,
		"voucher_no": d.name,
		"voucher_detail_no": d.name,
		"actual_qty": 0,
		"stock_uom": d.stock_uom,
		"incoming_rate": 0,
		"company": d.company,
		"batch_no": "",
		"serial_no": "",
		"project": "",
		"is_cancelled": d.docstatus==2 and "Yes" or "No"
	})

	sl_dict.update(args)
	return sl_dict

##
# Prepre the basic accounting ledger 
##
def prepare_gl(d, args):
	"""this method populates the common properties of a gl entry record"""
	# frappe.throw(frappe.as_json(d))
	gl_dict = frappe._dict({
		'company': d.company,
		'posting_date': d.posting_date,
		'fiscal_year': get_fiscal_year(d.posting_date, company=d.company)[0],
		'voucher_type': d.doctype,
		'voucher_no': d.name,
		'remarks': '',
		'debit': 0,
		'credit': 0,
		'debit_in_account_currency': 0,
		'credit_in_account_currency': 0,
		'is_opening': "No",
		'party_type': None,
		'party': None,
		'project': ""
	})
	gl_dict.update(args)

	return gl_dict

def cancel_budget_entry(reference_type, reference_no):
	if frappe.db.exists("Consumed Budget", {"reference_type":str(reference_type), "reference_no":str(reference_no)}):
		doc = frappe.get_doc("Consumed Budget", {"reference_type":str(reference_type), "reference_no":str(reference_no)})
		doc.cancel()
		frappe.db.sql("delete from `tabConsumed Budget` where reference_type = %s and reference_no = %s",(str(reference_type), str(reference_no)))
	if frappe.db.exists("Commited Budget", {"reference_type":str(reference_type), "reference_no":str(reference_no)}):
		doc = frappe.get_doc("Commited Budget", {"reference_type":str(reference_type), "reference_no":str(reference_no)})
		doc.cancel()
		frappe.db.sql("delete from `tabCommitted Budget` where reference_type = %s and reference_no = %s",(str(reference_type), str(reference_no)))
	return

def check_budget_available_for_reappropiation(cost_center, budget_account, transaction_date, amount):
	budget_against = frappe.db.get_single_value("Accounts Settings", "budget_level")
	if not budget_against:
		frappe.throw("Budget Level not set in Accounts Settings")
	cond = ""
	if budget_against == "Cost Center":
		cond += " and b.budget_against = '{}' and b.cost_center = '{}'".format(budget_against, cost_center)
	else:
		cond += " and b.budget_against = '{}'".format(budget_against)
	budget_amount = frappe.db.sql("select b.action_if_annual_budget_exceeded as action, \
					ba.budget_check, ba.budget_amount, b.deviation \
					from `tabBudget` b, `tabBudget Account` ba \
					where b.docstatus = 1 \
					and ba.parent = b.name and ba.account= '{}' \
					and b.fiscal_year = '{}' {} ".format(budget_account, str(transaction_date)[0:4], cond), as_dict=True)
 
	if budget_amount:
		if budget_against == "Cost Center":
			committed = frappe.db.sql("select SUM(cb.amount) as total from `tabCommitted Budget` cb where cb.account=%s and cb.cost_center=%s and cb.po_date between %s and %s", (budget_account, cost_center, str(transaction_date)[0:4] + "-01-01", str(transaction_date)[0:4] + "-12-31"), as_dict=True)
			consumed = frappe.db.sql("select SUM(cb.amount) as total from `tabConsumed Budget` cb where cb.account=%s and cb.cost_center=%s and cb.po_date between %s and %s", (budget_account, cost_center, str(transaction_date)[0:4] + "-01-01", str(transaction_date)[0:4] + "-12-31"), as_dict=True)
		else:
			committed = frappe.db.sql("select SUM(cb.amount) as total from `tabCommitted Budget` cb where cb.account=%s and cb.po_date between %s and %s", (budget_account, str(transaction_date)[0:4] + "-01-01", str(transaction_date)[0:4] + "-12-31"), as_dict=True)
			consumed = frappe.db.sql("select SUM(cb.amount) as total from `tabConsumed Budget` cb where cb.account=%s and cb.po_date between %s and %s", (budget_account, str(transaction_date)[0:4] + "-01-01", str(transaction_date)[0:4] + "-12-31"), as_dict=True)
		if consumed and committed:
			if flt(consumed[0].total) > flt(committed[0].total):
				committed = consumed
			total_consumed_amount = flt(committed[0].total) + flt(amount)
			if flt(total_consumed_amount) > flt(budget_amount[0].budget_amount):
				frappe.msgprint("Total Amount consumed: {} and Budget Amount:  {}".format(total_consumed_amount, budget_amount[0].budget_amount))
				frappe.throw("Not enough budget in <b>" + str(budget_account) + "</b>. The budget is exceeded by <b>" + str(flt(total_consumed_amount) - flt(budget_amount[0].budget_amount)) + "</b>")
	else:
		frappe.throw("There is no budget allocated in <b>" + str(budget_account) + "</b>")

##
# Check budget availability in the budget head
##
def check_budget_available(cost_center, budget_account, transaction_date, amount, project = None):
	consumed=committed= None
	if project:
		budget_amount = frappe.db.sql("select b.action_if_annual_budget_exceeded as action, \
						ba.budget_check, ba.budget_amount, b.deviation \
						from `tabBudget` b, `tabBudget Cost Center` ba \
						where b.docstatus = 1 \
						and ba.parent = b.name and ba.cost_center= '{}' \
						and b.fiscal_year = '{}' \
						and b.project = '{}' ".format(cost_center, str(transaction_date)[0:4], project), as_dict=True)
		if budget_amount:
			committed = frappe.db.sql("select SUM(cb.amount) as total from `tabCommitted Budget` cb where cb.cost_center=%s and cb.project=%s and cb.reference_date between %s and %s", (cost_center, project, str(transaction_date)[0:4] + "-01-01", str(transaction_date)[0:4] + "-12-31"), as_dict=True)
			consumed = frappe.db.sql("select SUM(cb.amount) as total from `tabConsumed Budget` cb where cb.cost_center=%s and cb.project=%s and cb.reference_date between %s and %s", (cost_center, project, str(transaction_date)[0:4] + "-01-01", str(transaction_date)[0:4] + "-12-31"), as_dict=True)
		msg = " Project: <b> " + str(project) +"</b>, for Cost Center :  <b>" + str(cost_center) + "</b> level for <b>" + str(transaction_date)[0:4] + "</b>"
	else:
		bud_acc_dtl = frappe.get_doc("Account", budget_account)
		if bud_acc_dtl.has_linked_budget == 1:
			budget_account = bud_acc_dtl.linked_budget
		#Check for Ignore Budget
		if bud_acc_dtl.budget_check:
			return
		#Check if Budget Account is Centralized
		if bud_acc_dtl.is_centralized_budget:
			cost_center = bud_acc_dtl.cost_center
		else:
			cc_doc = frappe.get_doc("Cost Center", cost_center)
			if cc_doc.use_budget_from_parent:
				cost_center = cc_doc.parent_cost_center
		
		budget_amount = frappe.db.sql("select b.action_if_annual_budget_exceeded as action, \
						ba.budget_check, ba.budget_amount, b.deviation \
						from `tabBudget` b, `tabBudget Account` ba \
						where b.docstatus = 1 \
						and ba.parent = b.name and ba.account= '{}' \
						and b.fiscal_year = '{}' \
						and b.cost_center = '{}' ".format(budget_account, str(transaction_date)[0:4], cost_center), as_dict=True)
		if budget_amount:
			committed = frappe.db.sql("select SUM(cb.amount) as total from `tabCommitted Budget` cb where cb.account=%s and cb.cost_center=%s and cb.reference_date between %s and %s", (budget_account, cost_center, str(transaction_date)[0:4] + "-01-01", str(transaction_date)[0:4] + "-12-31"), as_dict=True)
			consumed = frappe.db.sql("select SUM(cb.amount) as total from `tabConsumed Budget` cb where cb.account=%s and cb.cost_center=%s and cb.reference_date between %s and %s", (budget_account, cost_center, str(transaction_date)[0:4] + "-01-01", str(transaction_date)[0:4] + "-12-31"), as_dict=True)
		msg = "Account: <b>" + str(budget_account) + "</b> set at <b>" + str(cost_center) + "</b> level for <b>" + str(transaction_date)[0:4] + "</b>"

	if not budget_amount:
		frappe.throw("There is no budget allocated for " + str(msg))

	ig_or_stop = budget_amount and budget_amount[0].action or None
	ig_or_stop_gl = budget_amount and budget_amount[0].budget_check or None
	if ig_or_stop == "Ignore" or ig_or_stop_gl == "Ignore":
		return
	else:
		if consumed and committed:
			if flt(consumed[0].total) > flt(committed[0].total):
				committed = consumed
			total_consumed_amount = flt(committed[0].total) + flt(amount)
			total_budget_with_deviation = 0.00
			if budget_amount[0].deviation > 0:
				total_budget_with_deviation = flt(budget_amount[0].budget_amount) + flt(budget_amount[0].deviation * budget_amount[0].budget_amount)/100
			else:
				total_budget_with_deviation = budget_amount[0].budget_amount
			if flt(total_consumed_amount) > flt(total_budget_with_deviation):
				balance_budget = flt(budget_amount[0].budget_amount) - flt(committed[0].total)
				insufficient_amount = flt(amount) - flt(balance_budget)
				frappe.throw("Budget of Nu. {} insufficient in <b> {} </b>. Total Budget is Nu. {}, total Consumed and Committed is Nu. {}. Balance budget is Nu. {}. ".format(insufficient_amount, str(msg), flt(budget_amount[0].budget_amount), flt(committed[0].total), balance_budget))
		else:
			frappe.throw("There is no budget allocated for " + str(msg))

@frappe.whitelist()
def get_cc_warehouse(branch):
	cc = get_branch_cc(branch)
	return {"cc": cc, "wh": None}	

@frappe.whitelist()
def get_branch_warehouse(branch):
	cc = get_branch_cc(branch)
	wh = frappe.db.get_value("Cost Center", cc, "warehouse")
	if not wh:
		frappe.throw("No warehosue linked with your branch or cost center")
	return wh

@frappe.whitelist()
def get_branch_from_cost_center(cost_center):
	return frappe.db.get_value("Branch", {"cost_center": cost_center, "disabled": 0}, "name")

@frappe.whitelist()
def kick_users():
	from frappe.sessions import clear_all_sessions
	clear_all_sessions()
	frappe.msgprint("Kicked All Out!")

def get_cc_customer(cc):
	customer = frappe.db.get_value("Customer", {"cost_center": cc}, "name")
	if not customer:
		frappe.throw("No Customer found for the Cost Center")
	return customer

def send_mail_to_role_branch(branch, role, message, subject=None):
	if not subject:
		subject = "Message from ERP System"
	users = frappe.db.sql_list("select a.parent from `tabHas Role` a, tabDefaultValue b where a.parent = b.parent and b.defvalue = %s and b.defkey = 'Branch' and a.role = %s", (branch, role))
	try:
		frappe.sendmail(recipients=users, subject=subject, message=message)
	except:
		pass

def check_account_frozen(posting_date):
	acc_frozen_upto = frappe.db.get_value('Accounts Settings', None, 'acc_frozen_upto')
	if acc_frozen_upto:
		frozen_accounts_modifier = frappe.db.get_value( 'Accounts Settings', None,'frozen_accounts_modifier')
		if getdate(posting_date) <= getdate(acc_frozen_upto) \
				and not frozen_accounts_modifier in frappe.get_roles():
			frappe.throw(_("You are not authorized to add or update entries before {0}").format(formatdate(acc_frozen_upto)))

	   
def sendmail(recipent, subject, message, sender=None):
	try:
		frappe.sendmail(recipients=recipent, sender=None, subject=subject, message=message)
	except:
		pass

def get_settings_value(setting_dt, company, field_name):
	value = frappe.db.sql("select {0} from `tab{1}` where company = '{2}'".format(field_name, setting_dt, company))
	return value and value[0][0] or None

###
# get_production_groups(group):
###
def get_production_groups(group):
	if not group:
		frappe.throw("Invalid Production Group")
	groups = []
	for a in frappe.db.sql("select item_sub_group from `tabProduction Group Item` where parent = %s", group, as_dict=1):
		groups.append(str(a.item_sub_group))
	return groups
				   
# Following code added by SHIV on 2021/05/13
def has_record_permission(doc, user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles: 
		return True

	if frappe.db.exists("Employee", {"branch":doc.branch, "user_id": user}):
		return True
	elif frappe.db.sql("""select count(*)
   				from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
	   			where e.user_id = '{user}'
		  		and ab.employee = e.name
				and bi.parent = ab.name
			 	and bi.branch = "{branch}"
			""".format(user=user, branch=doc.branch))[0][0]:
		return True
	else:
		return False 


def add_crm_role_to_crm_users():
	# Get all users with Account Type = "CRM"
	users = frappe.get_all("User", filters={"account_type": "CRM"}, fields=["name"])

	for user in users:
		# Check if the user already has the role
		if not frappe.db.exists("Has Role", {"parent": user.name, "role": "CRM User"}):
			# Assign the CRM User role
			frappe.get_doc({
				"doctype": "Has Role",
				"parent": user.name,
				"parenttype": "User",
				"parentfield": "roles",
				"role": "CRM User"
			}).insert(ignore_permissions=True)
			print(f"Role added to {user.name}")
		else:
			print(f"Role already exists for {user.name}")

	frappe.db.commit()
	print("Done assigning CRM User role to all CRM users.")

import frappe

def add_crm_role_and_keys_and_password():
	users = frappe.get_all(
		"User",
		filters={"account_type": "CRM"},
		fields=["name", "api_key"]
	)

	for user in users:
		user_doc = frappe.get_doc("User", user.name)

		# 1️⃣ Add CRM User role if missing
		if not frappe.db.exists(
			"Has Role",
			{"parent": user.name, "role": "CRM User"}
		):
			user_doc.append("roles", {
				"role": "CRM User"
			})

		# 2️⃣ Generate API Key if missing
		if not user_doc.api_key:
			user_doc.api_key = frappe.generate_hash(length=15)

		# 3️⃣ Generate API Secret if missing (SAFE way)
		if not frappe.db.get_value("User", user.name, "api_secret"):
			user_doc.api_secret = frappe.generate_hash(length=32)

		# 4️⃣ Set password
		user_doc.new_password = "2026"

		# Optional but recommended
		user_doc.must_change_password = 1

		user_doc.save(ignore_permissions=True)

		print(f"Updated user: {user.name}")

	frappe.db.commit()
	print("✅ CRM users updated successfully.")


#filtering child doctypes of doctype
@frappe.whitelist()
def filter_child_doctypes(doctype, txt, searchfield, start, page_len, filters):
	# frappe.throw("here")
	data = []
	if not filters.get("parent"):
		frappe.throw("Please select Document Type first.")
	
	return frappe.db.sql("""
	SELECT distinct options FROM `tabDocField` WHERE fieldtype = 'Table' AND parent = '{}';
	""".format(filters.get("parent")[0]))

def leave_approver():
	leaves = frappe.db.sql("""
		SELECT name, employee, posting_date
		FROM `tabLeave Application`
		WHERE workflow_state = 'Waiting Approval'
		  AND posting_date <= %s
	""", ("2026-01-20",), as_dict=True)

	for leave in leaves:
		# Employee cost center
		cost_center = frappe.db.get_value(
			"Employee", leave.employee, "cost_center"
		)
		if not cost_center:
			continue

		# Parent cost center
		parent_cc = frappe.db.get_value(
			"Cost Center", cost_center, "parent_cost_center"
		)
		if not parent_cc:
			continue

		# Approver user from settings
		approver_user = frappe.db.get_value(
			"Approver Settings",
			{"cost_center": parent_cc},
			"user_id"
		)
		if not approver_user:
			continue

		# Final approver employee details
		final_approver = frappe.db.get_value(
			"Employee",
			{"user_id": approver_user},
			["user_id", "employee_name", "designation"],
			as_dict=True
		)
		if not final_approver:
			continue

		# Update Leave Application
		frappe.db.set_value(
			"Leave Application",
			leave.name,
			{
				"leave_approver": final_approver.user_id,
				"leave_approver_name": final_approver.employee_name,
				"leave_approver_designation": final_approver.designation
			}
		)

		print(f"{leave.name} | CC: {cost_center} → {parent_cc}")
		# break

import csv
import frappe

@frappe.whitelist()
def fi_fix():
	# file_path = "/home/frappe/erp/apps/salary_advance_deductions.csv"
	file_path="/home/frappe/erp/apps/financial_institution_loan1.csv"

	with open(file_path, newline="", encoding="utf-8") as f:
		reader = csv.DictReader(f)

		for row in reader:
			employee = row.get("Employee")
			bank_branch = row.get("Bank Branch")
			amount = flt(row.get("Amount",0))
			
			# print(employee)

			result = frappe.db.sql(
				"""
				SELECT
					ss.name AS salary_structure,
					sd.name AS sd_name,
					sd.amount
				FROM `tabSalary Structure` ss
				JOIN `tabSalary Detail` sd
					ON ss.name = sd.parent
				WHERE
					ss.is_active = 'Yes'
					AND sd.salary_component = 'Financial Institution Loan'
					AND ss.employee = %s
					AND sd.amount = %s
				""",
				(employee, amount),
				as_dict=True
			)

			if result:
				frappe.db.sql(
					"""
					UPDATE `tabSalary Detail`
					SET bank_branch = %s
					WHERE name=%s
					""",
					(bank_branch, result[0]["sd_name"])
				)
				print('{}-{}-{}'.format(result[0]['salary_structure'],bank_branch,amount))
			# break

		frappe.db.commit()
			# break
	#         salary_structure = row["Salary Structure"]
	#         employee = row["Employee"]
	#         balance = flt(row["Balance"])

	#         # example action
	#         frappe.logger().info(
	#             f"SS: {salary_structure}, Emp: {employee}, Balance: {balance}"
	#         )

	#         # example update
	#         # frappe.db.set_value(
	#         #     "Salary Structure",
	#         #     salary_structure,
	#         #     "custom_salary_advance_balance",
	#         #     balance
	#         # )

	# frappe.db.commit()
	# return "Salary advance CSV processed successfully"
# @frappe.whitelist()
# def update_bank_in_sl():
# 	salary_struct = frappe.db.sql(
# 		"""
# 		SELECT
# 			name,
# 			reference_number,
# 			amount,
# 			bank_name,
# 			bank_account_type,
# 			bank_branch,
# 			reference_name,
# 			reference_type,parent
# 		FROM `tabSalary Detail`
# 		WHERE salary_component = 'Financial Institution Loan'
# 		AND parenttype = 'Salary Structure'
# 		""",
# 		as_dict=True
# 	)

# 	for i in salary_struct:
# 		# print('{}-{}'.format(i["parent"], i["amount"]))
# 		result = frappe.db.sql(
# 			"""
# 			SELECT
# 				ss.name AS salary_structure,
# 				sd.name AS sd_name,
# 				sd.amount
# 			FROM `tabSalary Slip` ss
# 			JOIN `tabSalary Detail` sd
# 				ON ss.name = sd.parent
# 			WHERE
# 				sd.salary_component = 'Financial Institution Loan'
# 				AND ss.salary_structure = %s
# 				AND sd.amount = %s
# 			""",
# 			(i["parent"], i["amount"]),
# 			as_dict=True
# 		)

# 		# print(result)

# 		if result:
# 			# print(result[0]["salary_structure"])

# 			frappe.db.sql(
# 					"""
# 					UPDATE `tabSalary Detail`
# 					SET
# 						bank_name = %s,
# 						bank_account_type = %s,
# 						reference_name = %s,
# 						reference_type = %s,
# 						reference_number = %s,
# 						bank_branch= %s
# 					WHERE name = %s
# 					""",
# 					(
# 						i.bank_name,
# 						i.bank_account_type,
# 						i.reference_name,
# 						i.reference_type,
# 						i.bank_branch
# 						result[0]["sd_name"]
# 					)
# 				)
# 				print("{}-{}".format(i.,i.amount))
# 		break

# 	frappe.db.commit()

def update_bank_in_sl():
	salary_struct = frappe.db.sql(
		"""
		SELECT
			name,
			reference_number,
			amount,
			bank_name,
			bank_account_type,
			bank_branch,
			reference_name,
			reference_type,
			parent
		FROM `tabSalary Detail`
		WHERE salary_component = 'Financial Institution Loan'
		AND parenttype = 'Salary Structure'
		""",
		as_dict=True
	)

	for i in salary_struct:
		result = frappe.db.sql(
			"""
			SELECT
				ss.name AS salary_structure,
				sd.name AS sd_name,
				sd.amount
			FROM `tabSalary Slip` ss
			JOIN `tabSalary Detail` sd
				ON ss.name = sd.parent
			WHERE
				sd.salary_component = 'Financial Institution Loan'
				AND ss.salary_structure = %s
				AND sd.amount = %s
			""",
			(i["parent"], i["amount"]),
			as_dict=True
		)

		if result:
			frappe.db.sql(
				"""
				UPDATE `tabSalary Detail`
				SET
					bank_name = %s,
					bank_account_type = %s,
					reference_name = %s,
					reference_type = %s,
					reference_number = %s,
					bank_branch = %s
				WHERE name = %s
				""",
				(
					i["bank_name"],
					i["bank_account_type"],
					i["reference_name"],
					i["reference_type"],
					i["reference_number"],
					i["bank_branch"],
					result[0]["sd_name"]
				)
			)

			print(
				"Updated SL Detail: {} | Amount: {}".format(
					result[0]["salary_structure"], i["amount"]
				)
			)
			# break

	frappe.db.commit()

def check_bank_in_sl():
	salary_struct = frappe.db.sql(
		"""
		SELECT name, reference_number, amount, bank_name, bank_account_type, bank_branch, reference_name, reference_type, parent FROM `tabSalary Detail` WHERE salary_component = 'Financial Institution Loan' AND
parenttype = 'Salary Structure' and bank_name='BOBL';
		""",
		as_dict=True
	)

	for i in salary_struct:
		result = frappe.db.sql(
			"""
			SELECT
				ss.name AS salary_structure,
				sd.name AS sd_name,
				sd.amount
			FROM `tabSalary Slip` ss
			JOIN `tabSalary Detail` sd
				ON ss.name = sd.parent
			WHERE
				sd.salary_component = 'Financial Institution Loan'
				AND ss.salary_structure = %s
				AND sd.amount = %s
			""",
			(i["parent"], i["amount"]),
			as_dict=True
		)

		if not result:
			print(i["parent"])
	# 		frappe.db.sql(
	# 			"""
	# 			UPDATE `tabSalary Detail`
	# 			SET
	# 				bank_name = %s,
	# 				bank_account_type = %s,
	# 				reference_name = %s,
	# 				reference_type = %s,
	# 				reference_number = %s,
	# 				bank_branch = %s
	# 			WHERE name = %s
	# 			""",
	# 			(
	# 				i["bank_name"],
	# 				i["bank_account_type"],
	# 				i["reference_name"],
	# 				i["reference_type"],
	# 				i["reference_number"],
	# 				i["bank_branch"],
	# 				result[0]["sd_name"]
	# 			)
	# 		)

	# 		print(
	# 			"Updated SL Detail: {} | Amount: {}".format(
	# 				result[0]["salary_structure"], i["amount"]
	# 			)
	# 		)
	# 		# break

	# frappe.db.commit()

def check_loan_acc():
	salary_struct = frappe.db.sql(
		"""
		SELECT parent, bank_name, reference_number
		FROM `tabSalary Detail`
		WHERE parenttype = 'Salary Structure'
		AND salary_component = 'Financial Institution Loan'
		""",
		as_dict=True
	)

	for idx, i in enumerate(salary_struct, start=1):
		result = frappe.db.sql(
			"""
			SELECT parent, bank_name, reference_number
			FROM `tabSalary Detail`
			WHERE parenttype = 'Salary Structure'
			AND salary_component = 'Financial Institution Loan'
			AND reference_number = %s
			""",
			(i["reference_number"],),
			as_dict=True
		)

		if result and i["bank_name"] == result[0]["bank_name"]:
			print(
				"{} - {} - {} - {} - {}".format(
					idx,
					i["parent"],
					i["reference_number"],
					result[0]["reference_number"],
					result[0]["bank_name"]
				)
			)

def check_duplicate_old_asset_codes():
	assets = frappe.db.get_all(
		"Asset",
		fields=["name", "old_asset_code"],
		filters={"old_asset_code": ["!=", ""]}
	)

	for asset in assets:
		duplicates = frappe.db.sql(
			"""
			SELECT name
			FROM `tabAsset`
			WHERE old_asset_code = %s
			  AND name != %s
			""",
			(asset.old_asset_code, asset.name),
			as_dict=True
		)

		if duplicates:
			print(
				f"Duplicate found → "
				f"old_asset_code: {asset.old_asset_code}, "
				f"Asset: {asset.name}, "
				f"Duplicates: {[d['name'] for d in duplicates]}"
			)


import csv
import frappe

def delete_duplicate_assets_not_cancelled():
	file_path = "/home/frappe/erp/duplicate_old_asset_codes_not_cancelled.csv"

	with open(file_path, newline="", encoding="utf-8") as f:
		reader = csv.reader(f)
		header = next(reader)  # skip header

		for row in reader:
			old_asset_code = row[0]

			# All columns except first (old code) and last (count) are asset names
			asset_names = [a.strip() for a in row[1:-1] if a.strip()]

			if len(asset_names) <= 1:
				print(f"\nOld Asset Code: {old_asset_code}")
				print(f"Only one asset found, skipping")
				continue

			keep_asset = asset_names[0]
			delete_assets = asset_names[1:]

			print(f"\nOld Asset Code: {old_asset_code}")
			print(f"Keeping: {keep_asset}")
			print(f"Deleting: {delete_assets}")

			for asset_name in delete_assets:
				if not frappe.db.exists("Asset", asset_name):
					print(f"❌ Asset not found: {asset_name}")
					continue

				doc = frappe.get_doc("Asset", asset_name)

				try:
					if doc.docstatus == 1:
						doc.cancel()

					frappe.delete_doc("Asset", asset_name, force=1)
					print(f"✅ Deleted: {asset_name}")

				except Exception:
					frappe.log_error(
						frappe.get_traceback(),
						f"Failed deleting Asset {asset_name}"
					)
					print(f"⚠️ Failed deleting: {asset_name}")

	frappe.db.commit()
	print("\n🎯 Duplicate assets cleanup completed")


# def map_clearance():
# 	bank = frappe.db.sql(
# 		"""
# 		select bpi.pi_number,bp.transaction_no,bp.posting_date
# 		from `tabBank Payment` bp inner join 
# 		`tabBank Payment Item` bpi on bp.name=bpi.parent 
# 		where bp.transaction_type='Journal Entry' group by bpi.pi_number;
# 		""",
# 		as_dict=True
# 	)

# 	for idx, i in enumerate(bank, start=1):
# 		frappe.db.sql("""
# 		update `tabJournal Entry` set cheque_no='{}' and cheque_date='{}' where name='{}'

# 		""".format(i.pi_number,i.posting_date,i.transaction_no))
# 		print(i.transaction_no)
# 		break
	

def map_clearance_jl():
	bank = frappe.db.sql(
		"""
		SELECT
			bpi.pi_number,
			bp.transaction_no,
			bp.posting_date,
			bpi.status,
			bpi.bank_journal_no
		FROM `tabBank Payment` bp
		INNER JOIN `tabBank Payment Item` bpi
			ON bp.name = bpi.parent
		WHERE bp.transaction_type = 'Journal Entry'
		and bp.posting_date between '2026-03-01' and '2026-04-31'
		and bpi.status='Completed'
		GROUP BY bpi.pi_number
		""",
		as_dict=True
	)

	for i in bank:
		frappe.db.sql(
			"""
			UPDATE `tabJournal Entry`
			SET
				cheque_no = %s,
				cheque_date = %s,
				clearance_date = %s
			WHERE name = %s
			""",
			(i.pi_number, i.posting_date,i.posting_date, i.transaction_no)
		)

		print(f" {i.transaction_no} {i.status} {i.bank_journal_no}")
		frappe.db.commit()
		# break

	# frappe.db.commit()
		

import frappe
from datetime import datetime

def update_payment_entry_reference_dates():
	# List of tuples: (payment_entry_name, reference_date)
	entries = [
	('PEBR260100007', '2026-01-01'),
	('PEBR260100013', '2026-01-01'),
	('PEBR260100022', '2026-01-01'),
	('PEBR260100024', '2026-01-01'),
	('PEBR260100032', '2026-01-01'),
	('PEBR260100075', '2026-01-05'),
	('PEBR260100076', '2026-01-05'),
	('PEBR260100077', '2026-01-05'),
	('PEBR260100086', '2026-01-05'),
	('PEBR260100087', '2026-01-05'),
	('PEBR260100088', '2026-01-05'),
	('PEBR260100089', '2026-01-05'),
	('PEBR260100091', '2026-01-05'),
	('PEBR260100092', '2026-01-05'),
	('PEBR260100098', '2026-01-05'),
	('PEBR260100102', '2026-01-05'),
	('PEBR260100103', '2026-01-05'),
	('PEBR260100104', '2026-01-05'),
	('PEBR260100105', '2026-01-05'),
	('PEBR260100106', '2026-01-05'),
	('PEBR260100107', '2026-01-05'),
	('PEBR260100108', '2026-01-05'),
	('PEBR260100109', '2026-01-05'),
	('PEBR260100110', '2026-01-05'),
	('PEBR260100111', '2026-01-05'),
	('PEBR260100112', '2026-01-05'),
	('PEBR260100113', '2026-01-05'),
	('PEBR260100114', '2026-01-05'),
	('PEBR260100115', '2026-01-05'),
	('PEBR260100126', '2026-01-06'),
	('PEBR260100130', '2026-01-05'),
	('PEBR260100131', '2026-01-06'),
	('PEBR260100132', '2026-01-06'),
	('PEBR260100133', '2026-01-06'),
	('PEBR260100134', '2026-01-06'),
	('PEBR260100135', '2026-01-06'),
	('PEBR260100136', '2026-01-06'),
	('PEBR260100139', '2026-01-06'),
	('PEBR260100140', '2026-01-06'),
	('PEBR260100141', '2026-01-06'),
	('PEBR260100142', '2026-01-06'),
	('PEBR260100144', '2026-01-06'),
	('PEBR260100146', '2026-01-06'),
	('PEBR260100147', '2026-01-06'),
	('PEBR260100148', '2026-01-06'),
	('PEBR260100149', '2026-01-06'),
	('PEBR260100150', '2026-01-06'),
	('PEBR260100151', '2026-01-06'),
	('PEBR260100152', '2026-01-06'),
	('PEBR260100154', '2026-01-06'),
	('PEBR260100155', '2026-01-06'),
	('PEBR260100156', '2026-01-06'),
	('PEBR260100159', '2026-01-07'),
	('PEBR260100160', '2026-01-07'),
	('PEBR260100161', '2026-01-07'),
	('PEBR260100162', '2026-01-07'),
	('PEBR260100163', '2026-01-07'),
	('PEBR260100164', '2026-01-07'),
	('PEBR260100165', '2026-01-07'),
	('PEBR260100166', '2026-01-07'),
	('PEBR260100167', '2026-01-07'),
	('PEBR260100168', '2026-01-07'),
	('PEBR260100169', '2026-01-07'),
	('PEBR260100170', '2026-01-07'),
	('PEBR260100173', '2026-01-07'),
	('PEBR260100174', '2026-01-07'),
	('PEBR260100175', '2026-01-07'),
	('PEBR260100176', '2026-01-07'),
	('PEBR260100177', '2026-01-07'),
	('PEBR260100178', '2026-01-07'),
	('PEBR260100179', '2026-01-07'),
	('PEBR260100180', '2026-01-08'),
	('PEBR260100181', '2026-01-08'),
	('PEBR260100182', '2026-01-08'),
	('PEBR260100183', '2026-01-08'),
	('PEBR260100184', '2026-01-08'),
	('PEBR260100185', '2026-01-08'),
	('PEBR260100186', '2026-01-08'),
	('PEBR260100187', '2026-01-08'),
	('PEBR260100188', '2026-01-08'),
	('PEBR260100189', '2026-01-08'),
	('PEBR260100190', '2026-01-08'),
	('PEBR260100191', '2026-01-08'),
	('PEBR260100192', '2026-01-08'),
	('PEBR260100193', '2026-01-08'),
	('PEBR260100194', '2026-01-08'),
	('PEBR260100195', '2026-01-05'),
	('PEBR260100196', '2026-01-08'),
	('PEBR260100197', '2026-01-08'),
	('PEBR260100198', '2026-01-08'),
	('PEBR260100199', '2026-01-08'),
	('PEBR260100200', '2026-01-08'),
	('PEBR260100201', '2026-01-08'),
	('PEBR260100202', '2026-01-08'),
	('PEBR260100203', '2026-01-08'),
	('PEBR260100204', '2026-01-09'),
	('PEBR260100205', '2026-01-09'),
	('PEBR260100206', '2026-01-09'),
	('PEBR260100207', '2026-01-09'),
	('PEBR260100208', '2026-01-09'),
	('PEBR260100209', '2026-01-09'),
	('PEBR260100210', '2026-01-09'),
	('PEBR260100211', '2026-01-09'),
	('PEBR260100212', '2026-01-09'),
	('PEBR260100213', '2026-01-09'),
	('PEBR260100214', '2026-01-09'),
	('PEBR260100215', '2026-01-09'),
	('PEBR260100216', '2026-01-09'),
	('PEBR260100217', '2026-01-09'),
	('PEBR260100218', '2026-01-09'),
	('PEBR260100219', '2026-01-09'),
	('PEBR260100220', '2026-01-09'),
	('PEBR260100221', '2026-01-09'),
	('PEBR260100222', '2026-01-09'),
	('PEBR260100223', '2026-01-09'),
	('PEBR260100224', '2026-01-09'),
	('PEBR260100225', '2026-01-09')
	]


	for pe_name, ref_date_str in entries:
		# Convert string to date object
		ref_date = datetime.strptime(ref_date_str, "%Y-%m-%d").date()

		# Update reference_date in Payment Entry
		frappe.db.set_value("Payment Entry", pe_name, "reference_date", ref_date)
		print(f"Updated {pe_name} -> {ref_date_str}")
		
		# frappe.db.commit()
		# break

	# Commit changes to database
	frappe.db.commit()

def update_sales_order():
	# List of tuples: (sales_order_name, additional_cost)
	entries = [
		('SO25123056-1', 867.15),
		('SO26010024', 144.53),
		('SO26010029', 361.31),
		('SO26010036', 115.62),
		('SO26010039', 144.53),
		('SO26010114', 122.85),
		('SO26010116', 433.58),
		('SO26010121', 30.21),
		('SO26010134', 289.05),
		('SO26010136-1', 371.85),
		('SO26010141-1', 433.58),
		('SO26010142-1', 289.05),
		('SO26010145', 2664.93),
		('SO26010146', 86.72),
		('SO26010148', 142.14),
		('SO26010157', 71.07),
		('SO26010158', 247.90),
		('SO26010159', 71.07),
		('SO26010160', 213.21),
		('SO26010162', 142.14),
		('SO26010163', 71.07),
		('SO26010164', 142.14),
		('SO26010165', 71.07),
		('SO26010166', 60.41),
		('SO26010167', 71.07),
		('SO26010168', 131.48),
		('SO26010169', 170.55),
		('SO26010170', 127.92),
		('SO26010171', 71.07),
		('SO26010172', 142.14),
		('SO26010173', 71.07),
		('SO26010175', 30.00),
		('SO26010184', 284.28),
		('SO26010187', 71.07),
		('SO26010188', 56.85),
		('SO26010189', 56.85),
		('SO26010191', 56.85),
		('SO26010192', 142.14),
		('SO26010193', 71.07),
		('SO26010194', 71.07),
		('SO26010195', 142.14),
		('SO26010196', 142.14),
		('SO26010197', 71.07),
		('SO26010198', 56.85),
		('SO26010199', 71.07),
		('SO26010200', 71.07),
		('SO26010201', 113.70),
		('SO26010202', 60.41),
		('SO26010203', 127.92),
		('SO26010204', 71.07),
		('SO26010205', 56.85),
		('SO26010206', 56.85),
		('SO26010207', 71.07),
		('SO26010212', 143.41),
		('SO26010220', 142.14),
		('SO26010221', 56.85),
		('SO26010222', 71.07),
		('SO26010224', 213.21),
		('SO26010225', 142.14),
		('SO26010226', 14.34),
		('SO26010228', 129.10),
		('SO26010229', 113.70),
		('SO26010230', 113.70),
		('SO26010231', 142.14),
		('SO26010232', 71.07),
		('SO26010233', 56.85),
		('SO26010235', 71.07),
		('SO26010237', 56.85),
		('SO26010238', 56.85),
		('SO26010239', 71.07),
		('SO26010240', 56.85),
		('SO26010241', 71.07),
		('SO26010242', 71.07),
		('SO26010243', 71.07),
		('SO26010244', 71.07),
		('SO26010245', 142.14),
		('SO26010246', 142.14),
		('SO26010247', 142.14),
		('SO26010248', 71.07),
		('SO26010249', 284.28),
		('SO26010250', 113.70),
		('SO26010251', 142.14),
		('SO26010252', 56.85),
		('SO26010253', 56.85),
		('SO26010254', 71.07),
		('SO26010255', 142.14),
		('SO26010256', 71.07),
		('SO26010257', 56.85),
		('SO26010258', 71.07),
		('SO26010259', 63.96),
		('SO26010260', 71.07),
		('SO26010261', 71.07),
		('SO26010262', 56.85),
		('SO26010263', 71.07),
		('SO26010264', 56.85),
		('SO26010265', 60.41),
		('SO26010266', 71.07),
		('SO26010267', 56.85),
		('SO26010268', 142.14),
		('SO26010269', 142.14),
		('SO26010270', 71.07),
		('SO26010271', 71.07),
		('SO26010272', 213.21),
		('SO26010273', 56.85),
		('SO26010274', 71.07),
		('SO26010275', 56.85),
		('SO26010276', 284.28),
		('SO26010277', 56.85),
		('SO26010279', 56.85),
		('SO26010280', 71.07),
		('SO26010281', 56.85),
		('SO26010282', 71.07),
		('SO26010283', 56.85),
		('SO26010284', 71.07),
		('SO26010285', 56.85),
		('SO26010286', 71.07),
		('SO26010287', 56.85),
		('SO26010288', 71.07),
		('SO26010289', 71.07),
		('SO26010290', 71.07),
	]

	for so_name, amount in entries:
		doc = frappe.get_doc("Sales Order",so_name)
		doc.additional_cost = amount
		doc.save()
		# frappe.db.commit()
		print(f"Updated {so_name} -> {amount}")
		# break
		

	frappe.db.commit()

def update_sales_invoice():
	# List of tuples: (sales_order_name, additional_cost)
	entries = [
		('SI26010026', 145.0),
		('SI26010029', 145.0),
		('SI26010031', 145.0),
		('SI26010036', 123.95),
		('SI26010039', 123.95),
		('SI26010046', 145.0),
		('SI26010049', 145.0),
		('SI26010050', 145.0),
		('SI26010065', 144.53),
		('SI26010080', 145.0),
		('SI26010081', 145.0),
		('SI26010084', 145.0),
		('SI26010085', 145.0),
		('SI26010088', 116.0),
		('SI26010090', 115.62),
		('SI26010096', 144.53),
		('SI26010149', 123.95),
		('SI26010150', 144.53),
		('SI26010152', 144.53),
		('SI26010153', 198.32),
		('SI26010154', 123.95),
		('SI26010156', 123.95),
		('SI26010157', 123.95),
		('SI26010159', 71.07),
		('SI26010160', 71.07),
		('SI26010161', 71.07),
		('SI26010163', 30.21),
		('SI26010164', 144.53),
		('SI26010166', 144.53),
		('SI26010183', 144.53),
		('SI26010187', 144.53),
		('SI26010192', 144.53),
		('SI26010194', 144.53),
		('SI26010195', 144.53),
		('SI26010199', 144.53),
		('SI26010200', 99.16),
		('SI26010201', 123.95),
		('SI26010202', 144.53),
		('SI26010203', 144.53),
		('SI26010205', 123.95),
		('SI26010211', 144.53),
		('SI26010214', 71.07),
		('SI26010215', 144.53),
		('SI26010216', 71.07),
		('SI26010217', 123.95),
		('SI26010218', 71.07),
		('SI26010220', 231.24),
		('SI26010221', 231.24),
		('SI26010222', 115.62),
		('SI26010226', 71.07),
		('SI26010234', 122.85),
		('SI26010235', 115.62),
		('SI26010238', 115.62),
		('SI26010239', 71.07),
		('SI26010241', 144.53),
		('SI26010242', 144.53),
		('SI26010244', 71.07),
		('SI26010245', 144.53),
		('SI26010246', 144.53),
		('SI26010248', 144.53),
		('SI26010249', 71.07),
		('SI26010250', 71.07),
		('SI26010251', 144.53),
		('SI26010254', 71.07),
		('SI26010255', 144.53),
		('SI26010256', 71.07),
		('SI26010257', 71.07),
		('SI26010259', 71.07),
		('SI26010260', 71.07),
		('SI26010261', 71.07),
		('SI26010262', 71.07),
		('SI26010263', 60.41),
		('SI26010264', 71.07),
		('SI26010265', 71.07),
		('SI26010266', 60.41),
		('SI26010267', 144.53),
		('SI26010268', 144.53),
		('SI26010270', 56.85),
		('SI26010271', 56.85),
		('SI26010272', 56.85),
		('SI26010273', 71.07),
		('SI26010274', 56.85),
		('SI26010275', 71.07),
		('SI26010276', 71.07),
		('SI26010277', 71.07),
		('SI26010278', 71.07),
		('SI26010299', 123.95),
		('SI26010303', 123.95),
		('SI26010304', 71.07),
		('SI26010305', 71.07),
		('SI26010307', 71.07),
		('SI26010308', 71.07),
		('SI26010309', 71.07),
		('SI26010311', 123.95),
		('SI26010312', 123.95),
		('SI26010313', 86.72),
		('SI26010314', 71.07),
		('SI26010318', 56.85),
		('SI26010319', 123.95),
		('SI26010330', 56.85),
		('SI26010334', 56.85),
		('SI26010336', 144.53),
		('SI26010338', 144.53),
		('SI26010340', 144.53),
		('SI26010341', 144.53),
		('SI26010342', 144.53),
		('SI26010343', 115.62),
		('SI26010347', 231.24),
		('SI26010350', 71.07),
		('SI26010351', 71.07),
		('SI26010357', 71.07),
		('SI26010360', 71.07),
		('SI26010361', 71.07),
		('SI26010364', 123.95),
		('SI26010365', 71.07),
		('SI26010366', 71.07),
		('SI26010367', 71.07),
		('SI26010368', 144.53),
		('SI26010369', 71.07),
		('SI26010370', 71.07),
		('SI26010372', 56.85),
		('SI26010375', 71.07),
		('SI26010376', 71.07),
		('SI26010377', 56.85),
		('SI26010378', 56.85),
		('SI26010380', 60.41),
		('SI26010382', 71.07),
		('SI26010383', 123.95),
		('SI26010384', 56.85),
		('SI26010385', 123.95),
		('SI26010386', 71.07),
		('SI26010388', 56.85),
		('SI26010389', 56.85),
		('SI26010391', 71.07),
		('SI26010405', 71.07),
		('SI26010406', 71.07),
		('SI26010407', 56.85),
		('SI26010408', 71.07),
		('SI26010409', 123.95),
		('SI26010410', 71.07),
		('SI26010411', 71.07),
		('SI26010412', 71.07),
		('SI26010413', 71.07),
		('SI26010414', 144.53),
		('SI26010416', 71.07),
		('SI26010417', 123.95),
		('SI26010422', 123.95),
		('SI26010423', 123.95),
		('SI26010425', 56.85),
		('SI26010427', 56.85),
		('SI26010429', 123.95),
		('SI26010430', 144.53),
		('SI26010431', 99.16),
		('SI26010434', 144.53),
		('SI26010435', 56.85),
		('SI26010437', 144.53),
		('SI26010439', 56.85),
		('SI26010441', 105.36),
		('SI26010444', 144.53),
		('SI26010447', 144.53),
		('SI26010449', 115.62),
		('SI26010450', 71.07),
		('SI26010451', 71.07),
		('SI26010454', 71.07),
		('SI26010456', 56.85),
		('SI26010458', 71.07),
		('SI26010459', 56.85),
		('SI26010462', 56.85),
		('SI26010463', 71.07),
		('SI26010464', 56.85),
		('SI26010465', 71.07),
		('SI26010466', 71.07),
		('SI26010467', 71.07),
		('SI26010468', 71.07),
		('SI26010469', 105.36),
		('SI26010470', 123.95),
		('SI26010471', 71.07),
		('SI26010472', 71.07),
		('SI26010473', 105.36),
		('SI26010474', 71.07),
		('SI26010475', 71.07),
		('SI26010477', 71.07),
		('SI26010478', 71.07),
		('SI26010479', 71.07),
		('SI26010480', 71.07),
		('SI26010481', 71.07),
		('SI26010482', 71.07),
		('SI26010484', 71.07),
		('SI26010493', 56.85),
		('SI26010494', 56.85),
		('SI26010505', 123.95),
		('SI26010506', 123.95),
		('SI26010514', 231.24),
		('SI26010516', 71.07),
		('SI26010517', 71.07),
		('SI26010518', 56.85),
		('SI26010519', 56.85),
		('SI26010520', 71.07),
		('SI26010521', 71.07),
		('SI26010522', 71.07),
		('SI26010523', 71.07),
		('SI26010524', 99.16),
		('SI26010525', 56.85),
		('SI26010526', 71.07),
		('SI26010527', 123.95),
		('SI26010528', 63.96),
		('SI26010529', 123.95),
		('SI26010530', 71.07),
		('SI26010531', 71.07),
		('SI26010532', 56.85),
		('SI26010533', 144.53),
		('SI26010534', 71.07),
		('SI26010536', 56.85),
		('SI26010537', 60.41),
		('SI26010538', 71.07),
		('SI26010539', 56.85),
		('SI26010540', 123.95),
		('SI26010542', 144.53),
		('SI26010545', 71.07),
		('SI26010549', 71.07),
		('SI26010550', 71.07),
		('SI26010551', 71.07),
		('SI26010554', 71.07),
		('SI26010558', 56.85),
		('SI26010559', 71.07),
		('SI26010560', 71.07),
		('SI26010562', 71.07),
		('SI26010563', 56.85),
		('SI26010564', 71.07),
		('SI26010565', 123.95),
		('SI26010566', 71.07),
		('SI26010567', 99.16),
		('SI26010569', 99.16),
		('SI26010571', 105.36),
		('SI26010572', 56.85),
		('SI26010573', 56.85),
		('SI26010574', 71.07),
		('SI26010576', 56.85),
		('SI26010584', 71.07),
		('SI26010590', 56.85),
		('SI26010593', 144.53),
		('SI26010594', 71.07),
		('SI26010598', 56.85),
		('SI26010601', 71.07),
		('SI26010605', 144.53),
		('SI26010606', 56.85),
		('SI26010614', 144.53),
		('SI26010616', 71.07),
		('SI26010618', 71.07),
		('SI26010619', 71.07),
		('SI26010621', 71.07),
		('SI26010622', 71.07),
		('SI26010623', 71.07),
		('SI26010624', 71.07),
		('SI26010626', 72.26),
		('SI26010632', 105.36),
		('SI26010634', 105.36),
		('SI26010635', 123.95),
		('SI26010638', 99.16),
		('SI26010647', 144.53),
		('SI26010656', 231.24),
		('SI26010662', 144.53),
		('SI26010683', 144.53),
		('SI26010685', 144.53),
		('SI26010710', 144.53),
		('SI26010712', 144.53),
	]

	for si_name, amount in entries:
		doc = frappe.get_doc("Sales Invoice",si_name)
		doc.additional_cost = amount
		doc.save()
		# frappe.db.commit()
		print(f"Updated {si_name} -> {amount}")
		
		

	frappe.db.commit()


# def update_business_activity():
# 	gl_entries = frappe.db.sql('''
# 		select name, voucher_no, business_activity,
# 		account,cost_center,credit,debit from 
# 		`tabGL Entry` where voucher_type='Journal Entry';
# 	''')

# 	for i in gl_entries:
# 		business_activity=frappe.db.sql('''
# 			select business_activity from `tabJournal Entry Account` 
# 			where parent='{}' and cost_center='{}' 
# 			and account='{}' and credit='{}' and debit='{}';
# 		'''.format(i['voucher_no'],i['cost_center'],i['cost_center'],i['credit'],i['debit']))

# 		frappe.db.set_value("GL Entry",i['name'],{"business_activity":business_activity[0]})

# def update_business_activity():
# 	gl_entries = frappe.db.sql(
# 		"""
# 		SELECT
# 			name,
# 			voucher_no,
# 			account,
# 			cost_center,
# 			debit,
# 			credit
# 		FROM `tabGL Entry`
# 		WHERE voucher_type = 'Journal Entry'
# 		""",
# 		as_dict=True
# 	)

# 	for gl in gl_entries:
# 		ba = frappe.db.sql(
# 			"""
# 			SELECT business_activity
# 			FROM `tabJournal Entry Account`
# 			WHERE parent = %s
# 			  AND account = %s
# 			  AND cost_center = %s
# 			LIMIT 1

# 			select business_activity from `tabJournal Entry Account` 
# 			where parent='{}' and cost_center='{}' 
# 			and account='{}' and credit='{}' and debit='{}';
# 			""",
# 			(gl.voucher_no,  gl.cost_center,gl.account,gl.credit,gl.debit),
# 			as_dict=True
# 		)
# 		print('{}-{}-{}-{}-{}'.format(gl.name,ba[0].get("business_activity"),gl.cost_center,gl.credit,gl.debit))

# 	# 	if ba and ba[0].get("business_activity"):
# 	# 		print('{}-{}'.format(gl.))
# 	# 		# frappe.db.set_value(
# 	# 		# 	"GL Entry",
# 	# 		# 	gl.name,
# 	# 		# 	"business_activity",
# 	# 		# 	ba[0]["business_activity"],
# 	# 		# 	update_modified=False
# 	# 		# )

# 	# 	# frappe.db.commit()
# 	# 		# print('{}-{}'.format(ba[0].get("business_activity"),gl.name))
# 	# 		break

# 	# frappe.db.commit()

def update_business_activity():
	gl_entries = frappe.db.sql(
		"""
		SELECT
			name,
			voucher_no,
			account,
			cost_center,erp
			debit,
			credit
		FROM `tabGL Entry`
		WHERE voucher_type = 'Journal Entry'
		and posting_date between '2026-03-01' and '2026-04-03'
		""",
		as_dict=True
	)

	print(f"\nProcessing {len(gl_entries)} GL Entries\n")

	for gl in gl_entries:
		ba = frappe.db.sql(
			"""
			SELECT business_activity
			FROM `tabJournal Entry Account`
			WHERE parent = %s
			  AND account = %s
			  AND cost_center = %s
			  AND debit = %s
			  AND credit = %s
			""",
			(
				gl.voucher_no,
				gl.account,
				gl.cost_center,
				gl.debit,
				gl.credit,
			),
			as_dict=True
		)

		
		if ba and ba[0].get("business_activity"):
			frappe.db.set_value(
				"GL Entry",
				gl.name,
				"business_activity",
				ba[0]["business_activity"],
				
			)
			# frappe.db.commit()
			print(
				f"✔ {gl.name} | JE: {gl.voucher_no} | "
				f"BA: {ba[0]['business_activity']} | "
				f"CC: {gl.cost_center} | DR: {gl.debit} | CR: {gl.credit}"
			)

			# break
	frappe.db.commit()

def update_ba_si_activity():
	gl_entries = frappe.db.sql(
		"""
		SELECT
			name,
			voucher_no,
			account,
			cost_center,
			debit,
			credit
		FROM `tabGL Entry`
		WHERE voucher_type = 'Sales Invoice'
		and posting_date between '2026-03-01' and '2026-04-03'
		""",
		as_dict=True
	)

	print(f"\nProcessing {len(gl_entries)} GL Entries\n")

	for gl in gl_entries:
		sit = frappe.db.sql(
			"""
			SELECT item_code
			FROM `tabSales Invoice Item`
			WHERE parent = %s
			  AND income_account = %s
			  AND cost_center = %s
			  AND docstatus = 1
			LIMIT 1
			""",
			(gl.voucher_no, gl.account, gl.cost_center),
			as_dict=True
		)

		# 🚫 No matching item → skip safely
		if not sit:
			# print(
			# 	f"✖ NO ITEM | GL: {gl.name} | "
			# 	f"SI: {gl.voucher_no} | "
			# 	f"Acc: {gl.account} | CC: {gl.cost_center}"
			# )
			continue

		item_code = sit[0]["item_code"]
		ba = frappe.db.get_value("Item", item_code, "business_activity")

		# frappe.db.set_value("GL Entry",gl.name,'')
		frappe.db.set_value(
				"GL Entry",
				gl.name,
				"business_activity",
				ba,
				
			)
		# frappe.db.commit()

		print(
			f"✔ ITEM MATCH | GL: {gl.name} | "
			f"SI: {gl.voucher_no} | "
			f"Acc: {gl.account} | CC: {gl.cost_center} | "
			f"Item: {item_code} | BA: {ba}"
		)
	frappe.db.commit()
		
		# break

		# Uncomment when confident
		# frappe.db.set_value("GL Entry", gl.name, "business_activity", ba)
def update_ba_dn_activity():
	gl_entries = frappe.db.sql(
		"""
		SELECT
			name,
			voucher_no,
			account,
			cost_center,
			debit,
			credit
		FROM `tabGL Entry`
		WHERE voucher_type = 'Delivery Note'
		and posting_date between '2026-03-01' and '2026-04-03'
		and is_cancelled = 0
		""",
		as_dict=True
	)

	print(f"\nProcessing {len(gl_entries)} GL Entries\n")

	for gl in gl_entries:
		sit = frappe.db.sql(
			"""
			SELECT item_code
			FROM `tabDelivery Note Item`
			WHERE parent = %s
			  AND expense_account = %s
			  AND cost_center = %s
			LIMIT 1
			""",
			(gl.voucher_no, gl.account, gl.cost_center),
			as_dict=True
		)

		# 🚫 No matching item → skip safely
		if not sit:
			# print(
			# 	f"✖ NO ITEM | GL: {gl.name} | "
			# 	f"SI: {gl.voucher_no} | "
			# 	f"Acc: {gl.account} | CC: {gl.cost_center}"
			# )
			continue

		item_code = sit[0]["item_code"]
		ba = frappe.db.get_value("Item", item_code, "business_activity")

		
		frappe.db.set_value(
				"GL Entry",
				gl.name,
				"business_activity",
				ba,
				
			)
		
		# frappe.db.commit()
		print(
			f"✔ ITEM MATCH | GL: {gl.name} | "
			f"SI: {gl.voucher_no} | "
			f"Acc: {gl.account} | CC: {gl.cost_center} | "
			f"Item: {item_code} | BA: {ba}"
		)
		# break

		
	frappe.db.commit()

def update_ba_pi_activity():
	gl_entries = frappe.db.sql(
		"""
		SELECT
			name,
			voucher_no,
			account,
			cost_center,
			debit,
			credit
		FROM `tabGL Entry`
		WHERE voucher_type = 'Purchase Invoice'
		and posting_date between '2026-03-01' and '2026-04-03'
		and is_cancelled = 0 
		""",
		as_dict=True
	)

	print(f"\nProcessing {len(gl_entries)} GL Entries\n")

	for gl in gl_entries:
		sit = frappe.db.sql(
			"""
			SELECT item_code
			FROM `tabPurchase Invoice Item`
			WHERE parent = %s
			  AND expense_account = %s
			  AND cost_center = %s
			LIMIT 1
			""",
			(gl.voucher_no, gl.account, gl.cost_center),
			as_dict=True
		)

		# 🚫 No matching item → skip safely
		if not sit:
			# print(
			# 	f"✖ NO ITEM | GL: {gl.name} | "
			# 	f"SI: {gl.voucher_no} | "
			# 	f"Acc: {gl.account} | CC: {gl.cost_center}"
			# )
			continue

		item_code = sit[0]["item_code"]
		ba = frappe.db.get_value("Item", item_code, "business_activity")

		
		frappe.db.set_value(
				"GL Entry",
				gl.name,
				"business_activity",
				ba,
				
			)
		
		# frappe.db.commit()
		print(
			f"✔ ITEM MATCH | GL: {gl.name} | "
			f"SI: {gl.voucher_no} | "
			f"Acc: {gl.account} | CC: {gl.cost_center} | "
			f"Item: {item_code} | BA: {ba}"
		)
		# break

		
	frappe.db.commit()


def update_ba_stock_activity():
	gl_entries = frappe.db.sql(
		"""
		SELECT
			name,
			voucher_no,
			account,
			cost_center,
			debit,
			credit
		FROM `tabGL Entry`
		WHERE voucher_type = 'Hire Charge Invoice'
		  AND is_cancelled = 0
		""",
		as_dict=True
	)

	print(f"\nProcessing {len(gl_entries)} GL Entries\n")

	for gl in gl_entries:
		se = frappe.db.sql(
			"""
			SELECT business_activity
			FROM `tabStock Entry`
			WHERE name = %s
			LIMIT 1
			""",
			(gl.voucher_no,),   # 👈 tuple!
			as_dict=True
		)

		if not se or not se[0].get("business_activity"):
			print(
				f"✖ NO BA | GL: {gl.name} | "
				f"SE: {gl.voucher_no} | "
				f"Acc: {gl.account} | CC: {gl.cost_center}"
			)
			continue

		ba = se[0]["business_activity"]

		# Uncomment when ready
		frappe.db.set_value(
			"GL Entry",
			gl.name,
			"business_activity",
			ba
		)

		print(
			f"✔ BA SET | GL: {gl.name} | "
			f"SE: {gl.voucher_no} | "
			f"Acc: {gl.account} | CC: {gl.cost_center} | "
			f"BA: {ba}"
		)

	frappe.db.commit()


def update_cc_si_activity():
	gl_entries = frappe.db.sql(
		"""
		SELECT
			name,
			voucher_no
		FROM `tabGL Entry`
		WHERE voucher_type = 'Sales Invoice'
		and posting_date between '2026-03-01' and '2026-04-03'
		""",
		as_dict=True
	)

	print(f"\nProcessing {len(gl_entries)} GL Entries\n")

	for gl in gl_entries:
		# Get branch from Sales Invoice
		branch = frappe.db.get_value(
			"Sales Invoice",
			gl.voucher_no,
			"branch"
		)

		if not branch:
			print(f"⚠️ No branch found for SI: {gl.voucher_no}")
			continue

		# Get cost center from Branch
		cost_center = frappe.db.get_value(
			"Branch",
			branch,
			"cost_center"
		)

		if not cost_center:
			print(f"⚠️ No cost center for Branch: {branch}")
			continue

		# Update GL Entry cost center
		frappe.db.set_value(
			"GL Entry",
			gl.name,
			"cost_center",
			cost_center
		)

		# frappe.db.commit()

		print(f"✔ Updated GL Entry {gl.name} → {cost_center}")
		# break

	frappe.db.commit()

def update_cc_dn():
	gl_entries = frappe.db.sql(
		"""
		SELECT
			name,
			voucher_no
		FROM `tabGL Entry`
		WHERE voucher_type = 'Delivery Note'
		and posting_date between '2026-03-01' and '2026-04-03'
		""",
		as_dict=True
	)

	print(f"\nProcessing {len(gl_entries)} GL Entries\n")

	for gl in gl_entries:
		# Get branch from Sales Invoice
		branch = frappe.db.get_value(
			"Delivery Note",
			gl.voucher_no,
			"branch"
		)

		if not branch:
			print(f"⚠️ No branch found for SI: {gl.voucher_no}")
			continue

		# Get cost center from Branch
		cost_center = frappe.db.get_value(
			"Branch",
			branch,
			"cost_center"
		)

		if not cost_center:
			print(f"⚠️ No cost center for Branch: {branch}")
			continue

		#Update GL Entry cost center
		frappe.db.set_value(
			"GL Entry",
			gl.name,
			"cost_center",
			cost_center
		)

		# frappe.db.commit()

		print(f"✔ Updated GL Entry {gl.name} → {cost_center}")
		# break

	frappe.db.commit()

def update_cc_pe():
	gl_entries = frappe.db.sql(
		"""
		SELECT
			name,
			voucher_no
		FROM `tabGL Entry`
		WHERE voucher_type = 'Payment Entry'
		and posting_date between '2026-03-01' and '2026-04-03'
		""",
		as_dict=True
	)

	print(f"\nProcessing {len(gl_entries)} GL Entries\n")

	for gl in gl_entries:
		# Get branch from Sales Invoice
		branch = frappe.db.get_value(
			"Payment Entry",
			gl.voucher_no,
			"branch"
		)

		if not branch:
			print(f"⚠️ No branch found for SI: {gl.voucher_no}")
			continue

		# Get cost center from Branch
		cost_center = frappe.db.get_value(
			"Branch",
			branch,
			"cost_center"
		)

		if not cost_center:
			print(f"⚠️ No cost center for Branch: {branch}")
			continue

		#Update GL Entry cost center
		# frappe.db.set_value(
		# 	"GL Entry",
		# 	gl.name,
		# 	"cost_center",
		# 	cost_center
		# )

		# frappe.db.commit()

		print(f"✔ Updated GL Entry {gl.name} → {cost_center}")
		# break

	frappe.db.commit()


def update_cc_pi():
	gl_entries = frappe.db.sql(
		"""
		SELECT
			name,
			voucher_no
		FROM `tabGL Entry`
		WHERE voucher_type = 'Purchase Invoice'
		and posting_date between '2026-03-01' and '2026-04-03'
		""",
		as_dict=True
	)

	print(f"\nProcessing {len(gl_entries)} GL Entries\n")

	for gl in gl_entries:
		# Get branch from Sales Invoice
		branch = frappe.db.get_value(
			"Purchase Invoice",
			gl.voucher_no,
			"branch"
		)

		if not branch:
			print(f"⚠️ No branch found for SI: {gl.voucher_no}")
			continue

		# Get cost center from Branch
		cost_center = frappe.db.get_value(
			"Branch",
			branch,
			"cost_center"
		)

		if not cost_center:
			print(f"⚠️ No cost center for Branch: {branch}")
			continue

		#Update GL Entry cost center
		# frappe.db.set_value(
		# 	"GL Entry",
		# 	gl.name,
		# 	"cost_center",
		# 	cost_center
		# )

		# frappe.db.commit()

		print(f"✔ Updated GL Entry {gl.name} → {cost_center}")
		# break

	frappe.db.commit()

def update_cc_pi():
	gl_entries = frappe.db.sql(
		"""
		SELECT
			name,
			voucher_no
		FROM `tabGL Entry`
		WHERE voucher_type = 'Purchase Invoice'
		and posting_date >='2026-03-01' and posting_date <='2026-04-03'
		
		""",
		as_dict=True
	)

	print(f"\nProcessing {len(gl_entries)} GL Entries\n")

	for gl in gl_entries:
		# Get branch from Sales Invoice
		branch = frappe.db.get_value(
			"Purchase Invoice",
			gl.voucher_no,
			"branch"
		)

		if not branch:
			print(f"⚠️ No branch found for SI: {gl.voucher_no}")
			continue

		# Get cost center from Branch
		cost_center = frappe.db.get_value(
			"Branch",
			branch,
			"cost_center"
		)

		if not cost_center:
			print(f"⚠️ No cost center for Branch: {branch}")
			continue

		# Update GL Entry cost center
		frappe.db.set_value(
			"GL Entry",
			gl.name,
			"cost_center",
			cost_center
		)

		frappe.db.commit()

		print(f"✔ Updated GL Entry {gl.name} → {cost_center}")
		# break

	frappe.db.commit()

def update_cc_pi():
	gl_entries = frappe.db.sql(
		"""
		SELECT
			name,
			voucher_no
		FROM `tabGL Entry`
		WHERE voucher_type = 'Purchase Invoice'
		
		""",
		as_dict=True
	)

	print(f"\nProcessing {len(gl_entries)} GL Entries\n")

	for gl in gl_entries:
		# Get branch from Sales Invoice
		branch = frappe.db.get_value(
			"Purchase Invoice",
			gl.voucher_no,
			"branch"
		)

		if not branch:
			print(f"⚠️ No branch found for SI: {gl.voucher_no}")
			continue

		# Get cost center from Branch
		cost_center = frappe.db.get_value(
			"Branch",
			branch,
			"cost_center"
		)

		if not cost_center:
			print(f"⚠️ No cost center for Branch: {branch}")
			continue

		# Update GL Entry cost center
		frappe.db.set_value(
			"GL Entry",
			gl.name,
			"cost_center",
			cost_center
		)

		frappe.db.commit()

		print(f"✔ Updated GL Entry {gl.name} → {cost_center}")
		# break

	frappe.db.commit()

# def update_salary_struct():
# 	employee = frappe.db.sql(
# 		"""
# 		SELECT e.name AS employee,ss.name as ss FROM `tabEmployee` e inner join 
# 		`tabSalary Structure` ss on e.name=ss.employee 
# 		where e.date_of_joining > ss.from_date;
		
# 		""",
# 		as_dict=True
# 	)

	

# 	for e in employee:
# 		# Get branch from Sales Invoice
# 		date_of_joining = frappe.db.get_value(
# 			"Employee",
# 			gl.name,
# 			"date_of_joining"
# 		)

# 		if not date_of_joining:
# 			print(f"⚠️ No branch found for SI: {e.employee}")
# 			continue

		
# 		ss = frappe.db.get_value(
# 			"Salary Structure",
# 			e.ss,
# 			["is_active="Yes"]
# 		)

		

		
# 		if ss:
# 			frappe.db.set_value(
# 				"Salary Structure",
# 				gl.ss,
# 				"from_date",
# 				e.employee
# 			)

# 		frappe.db.commit()

# 		print(f"✔ Updated GL Entry {gl.name} → {cost_center}")
# 		# break

# 	frappe.db.commit()

def update_salary_struct():
	employees = frappe.db.sql(
		"""
		SELECT e.name AS employee, ss.name AS ss
		FROM `tabEmployee` e
		INNER JOIN `tabSalary Structure` ss
			ON e.name = ss.employee
		WHERE e.date_of_joining > ss.from_date
		  AND ss.is_active = 'Yes';
		""",
		as_dict=True
	)

	print(f"Processing {len(employees)} Salary Structures...\n")

	for e in employees:
		# Get Salary Structure from_date
		ss_from_date = frappe.db.get_value(
			"Salary Structure",
			e.ss,
			"from_date"
		)

		if not ss_from_date:
			print(f"⚠️ No from_date found for Salary Structure: {e.ss}")
			continue

		# Update Employee's date_of_joining to match Salary Structure's from_date
		frappe.db.set_value(
			"Employee",
			e.employee,  # Correct: update employee, not ss
			"date_of_joining",
			ss_from_date
		)

		print(f"✔ Updated Employee {e.employee} → date_of_joining: {ss_from_date}")
		# break

	# frappe.db.commit()
	# print("✅ All updates committed")


def map_clearance_pe():
	bank = frappe.db.sql(
		"""
		SELECT bpi.pi_number, bp.transaction_no, 
		bp.posting_date, bpi.status, bpi.bank_journal_no 
		FROM `tabBank Payment` bp INNER JOIN `tabBank Payment Item` bpi ON bp.name = bpi.parent 
		WHERE bp.transaction_type = 'Payment Entry' and 
		bp.posting_date between '2026-03-01' and '2026-04-31' and 
		bpi.status='Completed' GROUP BY bpi.pi_number;
		""",
		as_dict=True
	)

	for i in bank:

		clearance_date = frappe.db.sql(
			"""
			SELECT clearance_date FROM `tabPayment Entry`
			WHERE name = %s
			""",
			(i.transaction_no,),
			as_dict=True
		)

		if not clearance_date or not clearance_date[0].get("clearance_date"):
			frappe.db.sql(
				"""
				UPDATE `tabPayment Entry`
				SET clearance_date = %s
				WHERE name = %s
				""",
				(i.posting_date, i.transaction_no)
			)

			print(f" {i.transaction_no} {i.status} {i.bank_journal_no}")
			frappe.db.commit()
			# break

	# frappe.db.commit()

def correct_stock_ledger():
	data = frappe.db.sql("""
		SELECT voucher_no 
		FROM `tabGL Entry` 
		WHERE voucher_type = "Delivery Note"
		AND account = 'Cost of Goods Manufacture - NRDCL'
		AND credit > 0 
		AND is_cancelled = 0
	""", as_dict=True)

	for d in data:
		voucher_no = d.voucher_no
		if voucher_no in ["DN2026010743","DN2026010748"]:
			continue
		print(voucher_no)

		# Delete wrong GL Entries
		frappe.db.sql("""
		    DELETE FROM `tabGL Entry`
		    WHERE voucher_no = %s
		""", (voucher_no,))

		# Get Delivery Note
		doc = frappe.get_doc("Delivery Note", voucher_no)

		# Repost GL Entries properly
		doc.make_gl_entries()

	frappe.db.commit()
		# break

def repost_all_delivery_notes():
    # Get all affected Delivery Notes (same query you ran)
    vouchers = frappe.db.sql("""
        SELECT DISTINCT voucher_no
        FROM `tabGL Entry`
        WHERE voucher_type = "Delivery Note"
        AND account = 'Cost of Goods Manufacture - NRDCL'
        AND credit > 0
        AND is_cancelled = 0
    """, as_dict=True)

    for v in vouchers:
        try:
            # Create a Repost Item Valuation record
            doc = frappe.get_doc({
                "doctype": "Repost Item Valuation",
                "based_on": "Transaction",
                "voucher_type": "Delivery Note",
                "voucher_no": v.voucher_no,
                "allow_negative_stock": 0  # Optional: block negative stock
            })

            doc.insert(ignore_permissions=True)
            doc.submit()  # Queues it for processing
            print(f"Queued for repost: {v.voucher_no}")

        except Exception as e:
            print(f"Error: {v.voucher_no} -> {e}")

    frappe.db.commit()

import frappe
from datetime import date

def repost_all_delivery_notes_by_item_warehouse():
    # Fixed posting date
    fixed_posting_date = date(2026, 1, 1)

    # Get all affected items and warehouses from GL Entries
    entries = frappe.db.sql("""
        SELECT DISTINCT bpi.item_code, bpi.warehouse
        FROM `tabGL Entry` gl
        INNER JOIN `tabDelivery Note Item` bpi
            ON gl.voucher_no = bpi.parent
        WHERE gl.voucher_type = "Delivery Note"
          AND gl.account = 'Cost of Goods Manufacture - NRDCL'
          AND gl.credit > 0
          AND gl.is_cancelled = 0
    """, as_dict=True)

    for e in entries:
        try:
            # Create a Repost Item Valuation record for each item + warehouse
            doc = frappe.get_doc({
                "doctype": "Repost Item Valuation",
                "based_on": "Item and Warehouse",
                "item_code": e.item_code,
                "warehouse": e.warehouse,
                "posting_date": fixed_posting_date,
                "allow_negative_stock": 0  # Optional: block negative stock
            })

            doc.insert(ignore_permissions=True)
            doc.submit()  # Queues it for processing
            print(f"Queued for repost: Item {e.item_code}, Warehouse {e.warehouse}")

        except Exception as ex:
            print(f"Error: Item {e.item_code}, Warehouse {e.warehouse} -> {ex}")

    frappe.db.commit()


def repost_hire_charge_invoice():
	hire_charge= frappe.db.sql('''
		select name from `tabHire Charge Invoice` where docstatus=1;
	''',as_dict=True)

	for i in hire_charge:
		gl = frappe.db.sql('''
			select name,account,credit, debit from `tabGL Entry` where voucher_no=%s;
		''',(i['name']))

		print(f"{i['name']}, {gl}")

def cancel_asset_journals():
    jl_name = frappe.db.sql('''
        SELECT 
            jea.parent AS journal_entry,
            jea.reference_name AS asset_reference
        FROM `tabJournal Entry Account` jea
        LEFT JOIN `tabAsset` a
            ON jea.reference_name = a.name
        WHERE jea.reference_type = 'Asset'
        AND a.name IS NULL;
    ''', as_dict=True)

    count = 0

    for i in jl_name:
        try:
            print(f"Cancelling: {i['journal_entry']}")

            jl_doc = frappe.get_doc("Journal Entry", i['journal_entry'])
            jl_doc.cancel()

            count += 1

            # Commit after every 5 records
            if count % 5 == 0:
                frappe.db.commit()
                print("Committed batch of 5")

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), f"Failed for {i['journal_entry']}")

    # Final commit for remaining records
    frappe.db.commit()
    print("Final commit done")
