# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe
from frappe import _, msgprint, scrub
from frappe.model.document import Document
from frappe.utils import cint, cstr, flt, fmt_money, formatdate, get_link_to_form, nowdate, datetime, getdate
from erpnext.budget.doctype.budget.budget import validate_expense_against_budget

class BudgetReappropiation(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.budget_reappropiation_detail.budget_reappropiation_detail import BudgetReappropiationDetail
		from frappe.types import DF

		amended_from: DF.Link | None
		appropriation_on: DF.Date
		approver: DF.Link | None
		approver_designation: DF.Data | None
		approver_name: DF.Data | None
		budget_against: DF.Literal["Cost Center"]
		budget_type: DF.Link | None
		company: DF.Link | None
		fiscal_year: DF.Link
		from_cost_center: DF.Link | None
		from_project: DF.Link | None
		items: DF.Table[BudgetReappropiationDetail]
		remark: DF.Data | None
		to_cost_center: DF.Link | None
		to_project: DF.Link | None
		total_reappropiation_amount: DF.Currency
	# end: auto-generated types

	
	def validate(self):
		self.validate_budget()
		self.budget_check()
		self.set_broad_head_from_account()

	def on_submit(self):
		# Only implement cancel logic here when submitting
		self.budget_appropriate(cancel=False)

	def set_broad_head_from_account(self):
		"""Auto-set broad_head as parent_account of selected account"""
		for row in self.get("items"):  # Replace with your child table fieldname
			if row.from_account and not row.from_broad_head:
				parent_account = frappe.db.get_value("Account", row.from_account, "parent_account")
				if parent_account:
					row.from_broad_head = parent_account
				else:
					frappe.throw(f"Account {row.from_account} does not have a parent account")
			elif row.to_account and row.to_broad_head:
				# Optional: Validate that broad_head matches parent_account
				parent_account = frappe.db.get_value("Account", row.to_account, "parent_account")
				if parent_account and row.to_broad_head != parent_account:
					frappe.throw(f"Broad Head {row.to_broad_head} does not match parent account {parent_account} of {row.to_account}")	
	
	def validate_budget(self):
		budget_against_field = frappe.scrub(self.budget_against)
		from_budget_against = self.from_cost_center if self.budget_against == "Cost Center" else self.from_project
		to_budget_against = self.to_cost_center if self.budget_against == "Cost Center" else self.to_project
		total_amount = 0
		if not self.items:
			frappe.throw(_("Please provide Budget Head or Account to Appropriate budget"))

		for d in self.items:
			total_amount += flt(d.amount)
			if d.from_account:
				from_budget_exist = frappe.db.sql(
					"""
					select br.name, bra.account 
					from `tabBudget` br
					join `tabBudget Account` bra on bra.parent = br.name
					where br.docstatus = 1 
					and br.company = %s 
					and br.{budget_against_field} = %s
					and br.fiscal_year = %s 
					and bra.account = %s
					""".format(budget_against_field=budget_against_field),
					(self.company, from_budget_against, self.fiscal_year, d.from_account),
					as_dict=1,
				)
				if not from_budget_exist:
					frappe.throw(_(
						"Budget record does not exist against {0} '{1}' and account '{2}' for fiscal year {3}"
					).format(self.budget_against, from_budget_against, d.from_account, self.fiscal_year))
			
			if d.to_account:
				to_budget_exist = frappe.db.sql(
					"""
					select br.name, bra.account 
					from `tabBudget` br
					join `tabBudget Account` bra on bra.parent = br.name
					where br.docstatus = 1 
					and br.company = %s 
					and br.{budget_against_field} = %s
					and br.fiscal_year = %s 
					and bra.account = %s
					""".format(budget_against_field=budget_against_field),
					(self.company, to_budget_against, self.fiscal_year, d.to_account),
					as_dict=1,
				)
				if not to_budget_exist:
					frappe.throw(_(
						"Budget record does not exist against {0} '{1}' and account '{2}' for fiscal year {3}"
					).format(self.budget_against, to_budget_against, d.to_account, self.fiscal_year))
		
		self.total_reappropiation_amount = total_amount

	# def budget_check(self):
	# 	args = frappe._dict()
	# 	args.budget_against = self.budget_against
	# 	args.cost_center = self.from_cost_center if self.budget_against == "Cost Center" else None
	# 	args.project = self.from_project if self.budget_against == "Project" else None
	# 	args.fiscal_year = self.fiscal_year
	# 	args.posting_date = self.appropriation_on
	# 	args.company = self.company
		
	# 	try:
	# 		fiscal_start_year = int(self.fiscal_year.split("-")[0])
	# 	except (AttributeError, IndexError, ValueError):
	# 		frappe.throw(f"Invalid fiscal_year format. Expected 'YYYY-YY', got: {self.fiscal_year}")

	# 	for a in self.get('items'):
	# 		first_day = None
	# 		for month_id in range(1, 13):
	# 			month = datetime.date(2023, month_id, 1).strftime("%B")
	# 			if a.from_month == month:
	# 				month_num = str(month_id).zfill(2)
	# 				first_day = f"{fiscal_start_year}-{month_num}-01"
	# 				break
			
	# 		if not first_day:
	# 			frappe.throw(f"Invalid month '{a.from_month}' specified in item")

	# 		args.account = a.from_account
	# 		args.amount = a.amount
	# 		args.posting_date = first_day
	# 		args.budget_activity = a.from_budget_activity
	# 		args.budget_sub_activity = a.from_budget_sub_activity
	# 		args.source_of_fund = a.source_of_fund

	# 		validate_expense_against_budget(args)
	def budget_check(self):
		args = frappe._dict()
		args.budget_against = self.budget_against
		args.cost_center = self.from_cost_center if self.budget_against == "Cost Center" else None
		args.project = self.from_project if self.budget_against == "Project" else None
		args.fiscal_year = self.fiscal_year
		args.posting_date = self.appropriation_on
		args.company = self.company
		
		try:
			fiscal_start_year = int(self.fiscal_year.split("-")[0])
		except (AttributeError, IndexError, ValueError):
			frappe.throw(f"Invalid fiscal_year format. Expected 'YYYY-YY', got: {self.fiscal_year}")

		for a in self.get('items'):
			first_day = None
			# for month_id in range(1, 13):
			# 	month = datetime.date(2023, month_id, 1).strftime("%B")
			# 	if a.from_month == month:
			# 		month_num = str(month_id).zfill(2)
			# 		first_day = f"{fiscal_start_year}-{month_num}-01"
			# 		break
			
			# if not first_day:
			# 	frappe.throw(f"Invalid month '{a.from_month}' specified in item")

			args.account = a.from_account
			args.amount = a.amount
			# args.posting_date = first_day
			args.budget_activity = a.from_budget_activity
			args.budget_sub_activity = a.from_budget_sub_activity
			args.source_of_fund = a.source_of_fund

			validate_expense_against_budget(args)

	def budget_appropriate(self, cancel=False):
		if frappe.db.get_value("Fiscal Year", self.fiscal_year, "closed"):
			frappe.throw("Fiscal Year " + self.fiscal_year + " has already been closed")
		else:
			budget_against_field = frappe.scrub(self.budget_against)
			from_budget_against = self.from_cost_center if self.budget_against == "Cost Center" else self.from_project
			to_budget_against = self.to_cost_center if self.budget_against == "Cost Center" else self.to_project
			
			for d in self.items:
				from_month = d.from_month
				to_month = d.to_month
				if d.amount <= 0:
					frappe.throw("Budget appropriation Amount should be greater than 0 for record " + str(d.idx))
				
				# self.update_budget_release_reappropriation(
				# 	d,
				# 	budget_against_field,
				# 	from_budget_against,
				# 	to_budget_against,
				# 	cancel
				# )
				
				from_account_query = """
					SELECT ba.name, ba.account
					FROM `tabBudget` b
					JOIN `tabBudget Account` ba ON ba.parent = b.name
					WHERE b.docstatus < 2
					AND b.company = %s
					AND b.{budget_field} = %s
					AND b.fiscal_year = %s
					AND ba.account = %s
					AND ba.budget_activity = %s
					AND ba.budget_sub_activity = %s
					AND ba.source_of_fund = %s
				""".format(budget_field=budget_against_field)
				
				from_account_params = [self.company, from_budget_against, self.fiscal_year, d.from_account, d.from_budget_activity, d.from_budget_sub_activity, d.source_of_fund]
				# frappe.throw(str(from_account_query))
				
				if hasattr(d, 'from_budget_activity') and d.from_budget_activity:
					from_account_query += " AND ba.budget_activity = %s"
					from_account_params.append(d.from_budget_activity)
				if hasattr(d, 'from_budget_sub_activity') and d.from_budget_sub_activity:
					from_account_query += " AND ba.budget_sub_activity = %s"
					from_account_params.append(d.from_budget_sub_activity)
				
				from_account = frappe.db.sql(from_account_query, tuple(from_account_params), as_dict=1)
				
				monthly_budget_check = frappe.db.get_single_value("Budget Settings", "monthly_budget_check")
				
				if from_account:
					from_budget_account = frappe.get_doc("Budget Account", from_account[0].name)
					total = flt(from_budget_account.budget_amount) - flt(d.amount)
					budget_sent = flt(from_budget_account.budget_sent) + flt(d.amount)
					
					if cancel:
						total = flt(from_budget_account.budget_amount) + flt(d.amount)
						budget_sent = flt(from_budget_account.budget_sent) - flt(d.amount)
					
					from_budget_account.db_set("budget_sent", flt(budget_sent, 2))
					
					if monthly_budget_check:
						if from_month:
							if from_month =="January":
								if cancel:
									sent = flt(from_budget_account.bs_january) - flt(d.amount)
									from_budget_account.db_set("bs_january", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
								else:
									sent = flt(from_budget_account.bs_january) + flt(d.amount)
									from_budget_account.db_set("bs_january", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
							elif from_month =="February":
								if cancel:
									sent = flt(from_budget_account.bs_february) - flt(d.amount)
									from_budget_account.db_set("bs_february", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
								else:
									sent = flt(from_budget_account.bs_february) + flt(d.amount)
									from_budget_account.db_set("bs_february", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
							elif from_month =="March":
								if cancel:
									sent = flt(from_budget_account.bs_march) - flt(d.amount)
									from_budget_account.db_set("bs_march", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
								else:
									sent = flt(from_budget_account.bs_march) + flt(d.amount)
									from_budget_account.db_set("bs_march", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
							elif from_month =="April":
								if cancel:
									sent = flt(from_budget_account.bs_april) - flt(d.amount)
									from_budget_account.db_set("bs_april", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
								else:
									sent = flt(from_budget_account.bs_april) + flt(d.amount)
									from_budget_account.db_set("bs_april", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
							elif from_month =="May":
								if cancel:
									sent = flt(from_budget_account.bs_may) - flt(d.amount)
									from_budget_account.db_set("bs_may", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
								else:
									sent = flt(from_budget_account.bs_may) + flt(d.amount)
									from_budget_account.db_set("bs_may", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
							elif from_month =="June":
								if cancel:
									sent = flt(from_budget_account.bs_june) - flt(d.amount)
									from_budget_account.db_set("bs_june", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
								else:
									sent = flt(from_budget_account.bs_june) + flt(d.amount)
									from_budget_account.db_set("bs_june", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
							elif from_month =="July":
								if cancel:
									sent = flt(from_budget_account.bs_july) - flt(d.amount)
									from_budget_account.db_set("bs_july", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
								else:
									sent = flt(from_budget_account.bs_july) + flt(d.amount)
									from_budget_account.db_set("bs_july", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
							elif from_month =="August":
								if cancel:
									sent = flt(from_budget_account.bs_august) - flt(d.amount)
									from_budget_account.db_set("bs_august", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
								else:
									sent = flt(from_budget_account.bs_august) + flt(d.amount)
									from_budget_account.db_set("bs_august", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
							elif from_month =="September":
								if cancel:
									sent = flt(from_budget_account.bs_september) - flt(d.amount)
									from_budget_account.db_set("bs_september", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
								else:
									sent = flt(from_budget_account.bs_september) + flt(d.amount)
									from_budget_account.db_set("bs_september", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
							elif from_month =="October":
								if cancel:
									sent = flt(from_budget_account.bs_october) - flt(d.amount)
									from_budget_account.db_set("bs_october", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
								else:
									sent = flt(from_budget_account.bs_october) + flt(d.amount)
									from_budget_account.db_set("bs_october", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
							elif from_month =="November":
								if cancel:
									sent = flt(from_budget_account.bs_november) - flt(d.amount)
									from_budget_account.db_set("bs_november", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
								else:
									sent = flt(from_budget_account.bs_november) + flt(d.amount)
									from_budget_account.db_set("bs_november", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
							else:
								if cancel:
									sent = flt(from_budget_account.bs_december) - flt(d.amount)
									from_budget_account.db_set("bs_december", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
								else:
									sent = flt(from_budget_account.bs_december) + flt(d.amount)
									from_budget_account.db_set("bs_december", flt(sent,2))
									from_budget_account.db_set("budget_amount", flt(total,2))
						else:
							frappe.throw("Please Enter From Month")
					else:
						from_budget_account.db_set("budget_amount", flt(total,2))
				
				# TO ACCOUNT query with budget activity and budget sub-activity filters
				to_account_query = """
					SELECT ba.name, ba.account
					FROM `tabBudget` b
					JOIN `tabBudget Account` ba ON ba.parent = b.name
					WHERE b.docstatus < 2
					AND b.company = %s
					AND b.{budget_field} = %s
					AND b.fiscal_year = %s
					AND ba.account = %s
					AND ba.budget_activity = %s
					AND ba.budget_sub_activity = %s
					AND ba.source_of_fund = %s
				""".format(budget_field=budget_against_field)
				
				to_account_params = [self.company, to_budget_against, self.fiscal_year, d.to_account, d.to_budget_activity, d.to_budget_sub_activity, d.to_source_of_fund]
				# frappe.throw(str(to_account_query))
				
				# Add budget activity filter if available
				if hasattr(d, 'to_budget_activity') and d.to_budget_activity:
					to_account_query += " AND ba.budget_activity = %s"
					to_account_params.append(d.to_budget_activity)
				
				# Add budget sub-activity filter if available
				if hasattr(d, 'to_budget_sub_activity') and d.to_budget_sub_activity:
					to_account_query += " AND ba.budget_sub_activity = %s"
					to_account_params.append(d.to_budget_sub_activity)
				
				to_account = frappe.db.sql(to_account_query, tuple(to_account_params), as_dict=1)
				
				if to_account:
					to_budget_account = frappe.get_doc("Budget Account", to_account[0].name)
					total = flt(to_budget_account.budget_amount) + flt(d.amount)
					budget_received = flt(to_budget_account.budget_received) + flt(d.amount)
					
					if cancel:
						total = flt(to_budget_account.budget_amount) - flt(d.amount)
						budget_received = flt(to_budget_account.budget_received) - flt(d.amount)
					
					to_budget_account.db_set("budget_received", flt(budget_received, 2))
					
					if monthly_budget_check:
						if to_month:
							if to_month =="January":
								if cancel:
									received = flt(to_budget_account.br_january) - flt(d.amount)
									to_budget_account.db_set("br_january", received)
									to_budget_account.db_set("budget_amount", total)
								else:
									received = flt(to_budget_account.br_january) + flt(d.amount)
									to_budget_account.db_set("br_january", received)
									to_budget_account.db_set("budget_amount", total)
							elif to_month =="February":
								if cancel:
									received = flt(to_budget_account.br_february) - flt(d.amount)
									to_budget_account.db_set("br_february", received)
									to_budget_account.db_set("budget_amount", total)
								else:
									received = flt(to_budget_account.br_february) + flt(d.amount)
									to_budget_account.db_set("br_february", received)
									to_budget_account.db_set("budget_amount", total)
							elif to_month =="March":
								if cancel:
									received = flt(to_budget_account.br_march) - flt(d.amount)
									to_budget_account.db_set("br_march", received)
									to_budget_account.db_set("budget_amount", total)
								else:
									received = flt(to_budget_account.br_march) + flt(d.amount)
									to_budget_account.db_set("br_march", received)
									to_budget_account.db_set("budget_amount", total)
							elif to_month =="April":
								if cancel:
									received = flt(to_budget_account.br_april) - flt(d.amount)
									to_budget_account.db_set("br_april", received)
									to_budget_account.db_set("budget_amount", total)
								else:
									received = flt(to_budget_account.br_april) + flt(d.amount)
									to_budget_account.db_set("br_april", received)
									to_budget_account.db_set("budget_amount", total)
							elif to_month =="May":
								if cancel:
									received = flt(to_budget_account.br_may) - flt(d.amount)
									to_budget_account.db_set("br_may", received)
									to_budget_account.db_set("budget_amount", total)
								else:
									received = flt(to_budget_account.br_may) + flt(d.amount)
									to_budget_account.db_set("br_may", received)
									to_budget_account.db_set("budget_amount", total)
							elif to_month =="June":
								if cancel:
									received = flt(to_budget_account.br_june) - flt(d.amount)
									to_budget_account.db_set("br_june", received)
									to_budget_account.db_set("budget_amount", total)
								else:
									received = flt(to_budget_account.br_june) + flt(d.amount)
									to_budget_account.db_set("br_june", received)
									to_budget_account.db_set("budget_amount", total)
							elif to_month =="July":
								if cancel:
									received = flt(to_budget_account.br_july) - flt(d.amount)
									to_budget_account.db_set("br_july", received)
									to_budget_account.db_set("budget_amount", total)
								else:
									received = flt(to_budget_account.br_july) + flt(d.amount)
									to_budget_account.db_set("br_july", received)
									to_budget_account.db_set("budget_amount", total)
							elif to_month =="August":
								if cancel:
									received = flt(to_budget_account.br_august) - flt(d.amount)
									to_budget_account.db_set("br_august", received)
									to_budget_account.db_set("budget_amount", total)
								else:
									received = flt(to_budget_account.br_august) + flt(d.amount)
									to_budget_account.db_set("br_august", received)
									to_budget_account.db_set("budget_amount", total)
							elif to_month =="September":
								if cancel:
									received = flt(to_budget_account.br_september) - flt(d.amount)
									to_budget_account.db_set("br_september", received)
									to_budget_account.db_set("budget_amount", total)
								else:
									received = flt(to_budget_account.br_september) + flt(d.amount)
									to_budget_account.db_set("br_september", received)
									to_budget_account.db_set("budget_amount", total)
							elif to_month =="October":
								if cancel:
									received = flt(to_budget_account.br_october) - flt(d.amount)
									to_budget_account.db_set("br_october", received)
									to_budget_account.db_set("budget_amount", total)
								else:
									received = flt(to_budget_account.br_october) + flt(d.amount)
									to_budget_account.db_set("br_october", received)
									to_budget_account.db_set("budget_amount", total)
							elif to_month =="November":
								if cancel:
									received = flt(to_budget_account.br_november) - flt(d.amount)
									to_budget_account.db_set("br_november", received)
									to_budget_account.db_set("budget_amount", total)
								else:
									received = flt(to_budget_account.br_november) + flt(d.amount)
									to_budget_account.db_set("br_november", received)
									to_budget_account.db_set("budget_amount", total)
							else:
								if cancel:
									received = flt(to_budget_account.br_december) - flt(d.amount)
									to_budget_account.db_set("br_december", received)
									to_budget_account.db_set("budget_amount", total)
								else:
									received = flt(to_budget_account.br_december) + flt(d.amount)
									to_budget_account.db_set("br_december", received)
									to_budget_account.db_set("budget_amount", total)
						else:
							frappe.throw("Please Enter To Month")
					else:
						to_budget_account.db_set("budget_amount", total)
				
				# Create reappropriation details record
				app_details = frappe.new_doc("Reappropriation Details")
				app_details.flags.ignore_permissions = 1
				app_details.budget_against = self.budget_against
				app_details.from_cost_center = self.from_cost_center if self.budget_against == "Cost Center" else ""
				app_details.to_cost_center = self.to_cost_center if self.budget_against == "Cost Center" else ""
				app_details.from_account = d.from_account
				app_details.to_account = d.to_account
				app_details.from_project = self.from_project if self.budget_against == "Project" else ""
				app_details.to_project = self.to_project if self.budget_against == "Project" else ""
				
				# Add budget activity and sub-activity fields if they exist
				if hasattr(d, 'from_budget_activity'):
					app_details.from_budget_activity = d.from_budget_activity
				if hasattr(d, 'to_budget_activity'):
					app_details.to_budget_activity = d.to_budget_activity
				if hasattr(d, 'from_budget_sub_activity'):
					app_details.from_budget_sub_activity = d.from_budget_sub_activity
				if hasattr(d, 'to_budget_sub_activity'):
					app_details.to_budget_sub_activity = d.to_budget_sub_activity
				
				app_details.amount = flt(d.amount, 2)
				app_details.posting_date = nowdate()
				app_details.reference = self.name
				app_details.from_month = from_month if from_month else ""
				app_details.to_month = to_month if to_month else ""
				app_details.company = self.company
				app_details.fiscal_year = self.fiscal_year
				app_details.submit()

	def update_budget_release_reappropriation(
		self, d, budget_against_field,
		from_budget_against, to_budget_against,
		cancel=False
	):

		# ===============================
		# FROM SIDE (BUDGET SENT)
		# ===============================
		from_release = frappe.db.sql(f"""
			SELECT bra.name, br.name as parent
			FROM `tabBudget` br
			JOIN `tabBudget Account` bra ON bra.parent = br.name
			WHERE br.docstatus < 2
			AND br.company = %s
			AND br.{budget_against_field} = %s
			AND br.fiscal_year = %s
			AND bra.account = %s
			AND bra.budget_Activity =%s
			AND bra.budget_sub_activity =%s
			AND bra.source_of_fund = %s
		""", (self.company, from_budget_against, self.fiscal_year, d.from_account, d.from_budget_activity, d.from_budget_sub_activity, d.source_of_fund), as_dict=1)

		from_release = frappe.db.sql(f"""
			SELECT bra.name, br.name as parent
			FROM `tabBudget` br
			JOIN `tabBudget Account` bra ON bra.parent = br.name
			WHERE br.docstatus < 2
			AND br.company = %s
			AND br.{budget_against_field} = %s
			AND br.fiscal_year = %s
			AND bra.account = %s
		""", (self.company, from_budget_against, self.fiscal_year, d.from_account), as_dict=1)
		# frappe.throw(str(from_release))

		if from_release:
			bra_doc = frappe.get_doc("Budget Account", from_release[0].name)

			if cancel:
				sent = flt(bra_doc.budget_sent) - flt(d.amount)
				# sent = flt(bra_doc.budget_amount) + flt(d.amount)
			else:
				sent = flt(bra_doc.budget_sent) + flt(d.amount)
				# sent = flt(bra_doc.budget_amount) - flt(d.amount)

			bra_doc.db_set("budget_sent", flt(sent, 2))

			# # Update parent
			# parent_doc = frappe.get_doc("Budget", from_release[0].parent)

			# if cancel:
			# 	parent_doc.db_set("budget_amount", flt(parent_doc.budget_amount) + flt(d.amount))
			# else:
			# 	parent_doc.db_set("budget_amount", flt(parent_doc.budget_amount) - flt(d.amount))

		# ===============================
		# TO SIDE (BUDGET RECEIVED)
		# ===============================
		to_release = frappe.db.sql(f"""
			SELECT bra.name, br.name as parent
			FROM `tabBudget` br
			JOIN `tabBudget Account` bra ON bra.parent = br.name
			WHERE br.docstatus < 2
			AND br.company = %s
			AND br.{budget_against_field} = %s
			AND br.fiscal_year = %s
			AND bra.account = %s
			AND bra.budget_Activity =%s
			AND bra.budget_sub_activity =%s
			AND bra.source_of_fund = %s
		""", (self.company, to_budget_against, self.fiscal_year, d.to_account, d.to_budget_activity, d.to_budget_sub_activity, d.to_source_of_fund), as_dict=1)
		# frappe.throw(str(to_release))

		if to_release:
			bra_doc = frappe.get_doc("Budget Account", to_release[0].name)

			if cancel:
				received = flt(bra_doc.budget_received) - flt(d.amount)
				# received = flt(bra_doc.budget_amount) - flt(d.amount)
			else:
				received = flt(bra_doc.budget_received) + flt(d.amount)
				# received = flt(bra_doc.budget_amount) + flt(d.amount)

			bra_doc.db_set("budget_received", flt(received, 2))

			# # Update parent
			# parent_doc = frappe.get_doc("Budget", to_release[0].parent)

			# if cancel:
			# 	parent_doc.db_set("budget_amount", flt(parent_doc.budget_amount) - flt(d.amount))
			# else:
			# 	parent_doc.db_set("budget_amount", flt(parent_doc.budget_amount) + flt(d.amount))				

def get_permission_query_conditions(user=None):
    if not user:
        user = frappe.session.user

    roles = frappe.get_roles(user)

    if "System Manager" in roles:
        return ""

    if "Budget User" in roles:
        return f"""
            `tabSupplementary Budget`.owner = {frappe.db.escape(user)}
            AND `tabBudget Proposal`.workflow_state  IN('Draft','Waiting for Approval','Approved','Rejected')
        """

    if "Budget Approver" in roles:
        return """
            `tabSupplementary Budget`.workflow_state IN('Waiting for Approval')
        """

    return "1=0"