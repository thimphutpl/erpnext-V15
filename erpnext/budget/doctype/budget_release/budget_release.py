# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe
import datetime
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import add_months, flt, fmt_money, get_last_day, getdate, get_first_day

from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
)
from erpnext.accounts.utils import get_fiscal_year
from frappe.utils import get_link_to_form


class BudgetReleaseError(frappe.ValidationError):
	pass

class DuplicateBudgetReleaseError(frappe.ValidationError):
	pass


class BudgetRelease(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.budget_release_account.budget_release_account import BudgetReleaseAccount
		from frappe.types import DF

		accounts: DF.Table[BudgetReleaseAccount]
		action_if_accumulated_monthly_budget_exceeded: DF.Literal["", "Stop", "Warn", "Ignore"]
		action_if_accumulated_monthly_budget_exceeded_on_mr: DF.Literal["", "Stop", "Warn", "Ignore"]
		action_if_accumulated_monthly_budget_exceeded_on_po: DF.Literal["", "Stop", "Warn", "Ignore"]
		action_if_annual_budget_exceeded: DF.Literal["", "Stop", "Warn", "Ignore"]
		action_if_annual_budget_exceeded_on_mr: DF.Literal["", "Stop", "Warn", "Ignore"]
		action_if_annual_budget_exceeded_on_po: DF.Literal["", "Stop", "Warn", "Ignore"]
		actual_total: DF.Currency
		amended_from: DF.Link | None
		applicable_on_booking_actual_expenses: DF.Check
		applicable_on_material_request: DF.Check
		applicable_on_purchase_order: DF.Check
		approved_budget: DF.Currency
		branch: DF.Link | None
		budget_against: DF.Literal["Cost Center"]
		budget_balance: DF.Currency
		budget_id: DF.Link | None
		budget_type: DF.Data | None
		company: DF.Link
		cost_center: DF.Link | None
		current_balance: DF.Currency
		deviation: DF.Percent
		fiscal_year: DF.Link
		jv: DF.Link | None
		month: DF.Literal["", "July", "August", "September", "October", "November", "December", "January", "February", "March", "April", "May", "June"]
		monthly_distribution: DF.Link | None
		posting_date: DF.Date
		project: DF.Link | None
		project_name: DF.Data | None
		released_budget: DF.Currency
		supp_total: DF.Currency
	# end: auto-generated types

	def autoname(self):
		self.name = make_autoname(
			#self.get(frappe.scrub(self.budget_against)) + "/" + self.fiscal_year + "/.###"
			"BUDR" + "/" + self.fiscal_year + "/"+self.month+"/.###"
		)

	def validate(self):
		if not self.budget_id:
			frappe.throw(_("Budget Release should be created from Budget Proposal"), title=_("Incorrect Procedure"))
		if not self.get(frappe.scrub(self.budget_against)):
			frappe.msgprint(_("{0} is mandatory").format(self.budget_against), raise_exception=True)
		self.validate_duplicate()
		self.validate_accounts()
		self.set_null_value()
		self.validate_applicable_for()
		self.set_broad_head_from_account()
		# self.set_initial_budget()
		self.calculate_budget()
		if self.accounts:
			for item in self.accounts:
				if item.monthly_release:
					self.calculate_totals()
				elif item.at_hock:
					self.calculate_total_monthly()
		# self.validate_against_budget_proposal()
		self.validate_monthly_budget_release()

	def on_submit(self):
		self.post_journal_entry()
		self.update_budget_released_amount()
		self.create_budget_released_entries()

	def on_cancel(self):
		# Cancel all Budget Released Entries first
		self.cancel_budget_released_entries()
		
		self.update_budget_released_amount(cancel=1)
		""" ++++++++++ Ver 2.0.190509 Ends ++++++++++++ """
		self.ignore_linked_doctypes = (
			"GL Entry",
			"Payment Ledger Entry",
			"Stock Ledger Entry",
			"Repost Item Valuation",
			"Serial and Batch Bundle",
		)
		docstatus = frappe.db.get_value("Journal Entry", self.jv, "docstatus")
		if docstatus and docstatus != 2:
			frappe.throw("Cancel the Journal Entry " + str(self.jv) + " and proceed.")

		self.db_set("jv", None)

	def cancel_budget_released_entries(self):
		"""Cancel all Budget Released Entries linked to this Budget Release"""
		bre_entries = frappe.get_all("Budget Release Entry", 
			filters={"released_budget": self.name, "docstatus": 1},
			pluck="name")
		
		for bre_name in bre_entries:
			bre = frappe.get_doc("Budget Release Entry", bre_name)
			bre.cancel()
			frappe.db.commit()
		
		if bre_entries:
			frappe.msgprint(_("Cancelled {0} Budget Release Entry/Entries").format(len(bre_entries)))	

	def validate_monthly_budget_release(self):	
		for item in self.accounts:
				if item.monthly_release:
					self.calculate_totals()

	def set_broad_head_from_account(self):
		"""Auto-set broad_head as parent_account of selected account"""
		for row in self.get("accounts"):  # Replace with your child table fieldname
			if row.account and not row.broad_head:
				parent_account = frappe.db.get_value("Account", row.account, "parent_account")
				if parent_account:
					row.broad_head = parent_account
				else:
					frappe.throw(f"Account {row.account} does not have a parent account")
			elif row.account and row.broad_head:
				# Optional: Validate that broad_head matches parent_account
				parent_account = frappe.db.get_value("Account", row.account, "parent_account")
				if parent_account and row.broad_head != parent_account:
					frappe.throw(f"Broad Head {row.broad_head} does not match parent account {parent_account} of {row.account}")	

	def update_budget_released_amount(self, cancel=0):

		for release_row in self.accounts:

			# Find matching Budget Account row
			budget_account = frappe.db.get_value(
				"Budget Account",
				{
					"cost_center": self.cost_center,
					"budget_activity": release_row.budget_activity,
					"budget_sub_activity": release_row.budget_sub_activity,
					"source_of_fund": release_row.source_of_fund,
					"account": release_row.account
				},
				["name", "released_budget", "budget_amount"],
				as_dict=1
			)

			if not budget_account:
				continue

			current_released = budget_account.released_budget or 0
			current_budget_amount = budget_account.budget_amount or 0

			release_amount = release_row.released_budget or 0

			# On Submit
			if not cancel:
				new_released = release_amount
				# new_released = current_released + release_amount
				# new_budget_amount = current_budget_amount + release_amount

			# On Cancel
			else:
				new_released = release_amount
				# new_released = current_released - release_amount
				# new_budget_amount = current_budget_amount - release_amount

			frappe.db.set_value(
				"Budget Account",
				budget_account.name,
				{
					"released_budget": new_released,
					# "budget_amount": new_budget_amount
				}
			)
 
	def post_journal_entry(self):
		from frappe.utils import flt
		import frappe


		company = frappe.defaults.get_user_default("Company")
		expense_bank_account = frappe.db.get_value("Company", company, "default_mof_account")
		bra_account = frappe.db.get_value("Company", company, "budget_receive_account")

		if not expense_bank_account:
			frappe.throw("No Default Payable Account (Default MOF Account) set in Company")

		if not bra_account:
			frappe.throw("No Budget Receive Account set in Company")
		if expense_bank_account and bra_account:
			if self.accounts and len(self.accounts) > 0:
				source_of_fund = self.accounts[0].source_of_fund
				budget_activity = self.accounts[0].budget_activity
				budget_sub_activity = self.accounts[0].budget_sub_activity

			je = frappe.new_doc("Journal Entry")
			je.flags.ignore_permissions = 1
			je.title = self.name
			je.voucher_type = "Bank Entry"
			je.naming_series = "Bank Payment Voucher"
			je.remark = "Payment against: " + self.name
			je.posting_date = self.posting_date
			je.branch = self.branch
			je.company = company

			je.append("accounts", {
				"account": bra_account,
				"cost_center": self.cost_center,
				"reference_type": "Budget Release",
				"reference_name": self.name,
				"debit_in_account_currency": flt(self.released_budget),
				"debit": flt(self.released_budget),
				# "budget_activity": budget_activity,
				# "budget_sub_activity": budget_sub_activity,
				"source_of_fund": source_of_fund,
			})

			je.append("accounts", {
				"account": expense_bank_account,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.released_budget),
				"credit": flt(self.released_budget),
				# "budget_activity": budget_activity,
				# "budget_sub_activity": budget_sub_activity,
				"source_of_fund": source_of_fund,
			})

			je.insert(ignore_permissions=True)
			je.submit()

			self.db_set("jv", je.name)
			# frappe.msgprint(f"Journal Entry <b>{je.name}</b> created and linked successfully.")
			frappe.msgprint(
				f"Journal Entry {get_link_to_form('Journal Entry', je.name)} created and linked successfully."
			)
		else:
			frappe.throw("Define POL expense account in Maintenance Setting or Expense Bank in Branch")

	def create_budget_released_entries(self):
		"""Create Budget Release Entry for each account in the child table"""
		from frappe.utils import flt
		
		if not self.accounts:
			return
		
		created_entries = []
		
		for item in self.accounts:
			if flt(item.released_budget) <= 0:
				continue
				
			# Check if Budget Release Entry already exists for this combination
			existing_entry = frappe.db.exists("Budget Release Entry", {
				"budget_release": self.name,
				"account": item.account,
				"cost_center": self.cost_center,
				"budget_activity": item.budget_activity,
				"budget_sub_activity": item.budget_sub_activity,
				"source_of_fund": item.source_of_fund,
				"docstatus": ["!=", 2]  # Not cancelled
			})
			
			if existing_entry:
				frappe.msgprint(_("Budget Release Entry already exists for Account {0}").format(item.account))
				continue
			
			# Create new Budget Release Entry
			bre = frappe.new_doc("Budget Release Entry")
			bre.budget_release = self.name
			bre.budget_id = self.budget_id
			bre.fiscal_year = self.fiscal_year
			bre.month = self.month
			bre.posting_date = self.posting_date
			bre.company = self.company
			bre.cost_center = self.cost_center
			bre.branch = self.branch
			
			# Account details
			bre.account = item.account
			# bre.account_name = item.account_name
			# bre.account_number = item.account_number
			bre.broad_head = item.broad_head
			
			# Budget dimensions
			bre.budget_activity = item.budget_activity
			# bre.budget_activity_name = item.budget_activity_name
			bre.budget_sub_activity = item.budget_sub_activity
			# bre.budget_sub_activity_name = item.budget_sub_activity_name
			bre.source_of_fund = item.source_of_fund
			# bre.source_of_fund_name = item.source_of_fund_name
			
			# Amounts
			bre.approved_budget = flt(item.approved_budget)
			bre.released_budget = flt(item.released_budget)
			# bre.supplementary_budget = flt(item.supplementary_budget)
			# bre.budget_received = flt(item.budget_received)
			# bre.budget_sent = flt(item.budget_sent)
			# bre.budget_amount = flt(item.budget_amount)
			# bre.current_balance = flt(item.current_balance) if hasattr(item, 'current_balance') else 0
			# bre.budget_balance = flt(item.budget_balance) if hasattr(item, 'budget_balance') else 0
			
			# # Reference to Journal Entry
			# bre.journal_entry = self.jv
			
			bre.flags.ignore_permissions = 1
			bre.insert()
			bre.submit()
			
			created_entries.append(bre.name)
		
		# if created_entries:
		# 	frappe.msgprint(_("{0} Budget Release Entry/Entries created successfully: {1}").format(
		# 		len(created_entries), ", ".join(created_entries)
		# 	))		
 
	def validate_against_budget_proposal(self):
	
		budget_against_field = frappe.scrub(self.budget_against)
		budget_against = self.get(budget_against_field)
		for d in self.accounts:
			approved_budget = flt(d.approved_budget)
			released_budget = flt(d.released_budget)

			total_released_for_account = frappe.db.sql(
				"""
				SELECT SUM(IFNULL(ba.released_budget, 0)) AS total_released
				FROM `tabBudget Release` b
				JOIN `tabBudget Release Account` ba ON ba.parent = b.name
				WHERE
					b.docstatus = 1
					AND ba.account = %s
					AND b.company = %s
					AND b.fiscal_year = %s
					AND b.name != %s
				""",
				(d.account, self.company, self.fiscal_year, self.name),
				as_dict=1,
			)

			total_released_for_account = flt(total_released_for_account[0].total_released) if total_released_for_account else 0
			# new_total_release = total_released_for_account + released_budget
			new_total_release = released_budget
			if new_total_release > approved_budget:
				frappe.throw(
					_(
						"Released budget for Account <b>{0}</b> exceeds the approved budget of {1}. "
						"Total released so far {2}, Attempted release {3}."
					).format(
						d.account,
						frappe.format_value(approved_budget, {"fieldtype": "Currency"}),
						frappe.format_value(total_released_for_account, {"fieldtype": "Currency"}),
						frappe.format_value(released_budget, {"fieldtype": "Currency"}),
					)
				)


	def validate_duplicate(self):
		budget_against_field = frappe.scrub(self.budget_against)
		budget_against = self.get(budget_against_field)

		accounts = [d.account for d in self.accounts] or []
		existing_budget = frappe.db.sql(
			"""
			select
				b.name, ba.account from `tabBudget Release` b, `tabBudget Release Account` ba
			where
				ba.parent = b.name and b.docstatus < 2 and b.company = %s and %s=%s and
				b.fiscal_year=%s and month = %s and b.name != %s and ba.account in (%s) """
			% ("%s", budget_against_field, "%s", "%s", "%s", "%s", ",".join(["%s"] * len(accounts))),
			(self.company, budget_against, self.fiscal_year, self.month, self.name) + tuple(accounts),
			as_dict=1)
		if existing_budget:
			for d in existing_budget:
				frappe.msgprint(
					_(
						"Another Budget Release record '{0}' already exists against {1} '{2}' and account '{3}' for fiscal year {4}"
					).format(d.name, self.budget_against, budget_against, d.account, self.fiscal_year),raise_exception=True
				)

	def validate_accounts(self):
		account_list = []
		for d in self.get("accounts"):
			if d.account:
				account_details = frappe.db.get_value(
					"Account", d.account, ["is_group", "company", "report_type"], as_dict=1
				)

				if account_details.is_group:
					frappe.msgprint(_("Budget cannot be assigned against Group Account {0}").format(d.account), raise_exception=True)
				elif account_details.company != self.company:
					frappe.msgprint(_("Account {0} does not belongs to company {1}").format(d.account, self.company), raise_exception=True)
				'''
				elif account_details.report_type != "Profit and Loss":
					frappe.throw(
						_("Budget cannot be assigned against {0}, as it's not an Income or Expense account").format(
							d.account
						)
					)
				'''

				# if d.account in account_list:
				# 	frappe.msgprint(_("Account {0} has been entered multiple times").format(d.account), raise_exception=True)
				# else:
				# 	account_list.append(d.account)

	def set_null_value(self):
		if self.budget_against == "Cost Center":
			self.project = None
		else:
			self.cost_center = None

	def validate_applicable_for(self):
		if self.applicable_on_material_request and not (
			self.applicable_on_purchase_order and self.applicable_on_booking_actual_expenses
		):
			frappe.msgprint(
				_("Please enable Applicable on Purchase Order and Applicable on Booking Actual Expenses"), raise_exception=True
			)

		elif self.applicable_on_purchase_order and not (self.applicable_on_booking_actual_expenses):
			frappe.msgprint(_("Please enable Applicable on Booking Actual Expenses"), raise_exception=True)

		elif not (
			self.applicable_on_material_request
			or self.applicable_on_purchase_order
			or self.applicable_on_booking_actual_expenses
		):
			self.applicable_on_booking_actual_expenses = 1

	def calculate_budget(self):
		if self.accounts:
			for acc in self.accounts:
				acc.budget_amount = flt(acc.approved_budget) + flt(acc.supplementary_budget) + flt(acc.budget_received) - flt(acc.budget_sent)
				acc.db_set("budget_amount", acc.budget_amount)
	
	def calculate_totals(self):
		from frappe.utils import flt

		if not self.accounts:
			return
		cost_center = self.cost_center
		approved_budget = 0.0
		total_actual = 0.0
		total_supplementary = 0.0
		released_budget = 0.0

		for item in self.accounts:
			approved_budget += flt(item.approved_budget)
			total_actual += flt(item.budget_amount)
			total_supplementary += flt(item.supplementary_budget)
			released_budget += flt(item.released_budget)
			if item.monthly_release:
				if flt(item.released_budget, 0) > flt(item.approved_budget/ 12, 0) :
					frappe.throw("Monthly released amount cannot be greater than approved budget by 12")

		last_release = frappe.db.sql("""
			SELECT current_balance, budget_balance
			FROM `tabBudget Release`
			WHERE docstatus = 1 AND name != %s AND cost_center = %s
			ORDER BY creation DESC
			LIMIT 1
		""", (self.name, cost_center), as_dict=True)

		if not last_release:
			self.current_balance = flt(approved_budget) + flt(item.supplementary_budget) + flt(item.budget_received) - flt(item.budget_sent)
			self.budget_balance = flt(approved_budget) - flt(released_budget)
		else:
			last_budget_balance = flt(last_release[0].get("budget_balance") or 0.0)
			self.current_balance = last_budget_balance + flt(approved_budget) + flt(item.supplementary_budget) + flt(item.budget_received) - flt(item.budget_sent)
			self.budget_balance = last_budget_balance + flt(approved_budget) - flt(released_budget)

		self.approved_budget = approved_budget
		self.actual_total = total_actual
		self.supp_total = total_supplementary
		self.released_budget = released_budget
 
	def calculate_total_monthly(self):
		from frappe.utils import flt
		from frappe import _

		if not self.accounts:
			return

		cost_center = self.cost_center
		approved_budget = 0.0
		total_actual = 0.0
		total_supplementary = 0.0
		released_budget = 0.0

		for item in self.accounts:
			approved_budget += flt(item.approved_budget)
			total_actual += flt(item.budget_amount)
			total_supplementary += flt(item.supplementary_budget)
			released_budget += flt(item.released_budget)

			# --- Get the last month's budget balance for this account ---
			last_release = frappe.db.sql("""
				SELECT b.budget_balance
				FROM `tabBudget Release Account` ba
				JOIN `tabBudget Release` b ON b.name = ba.parent
				WHERE b.docstatus = 1
				AND b.cost_center = %s
				AND ba.parent_account = %s
				AND ba.account = %s
				AND ba.budget_activity = %s
				AND ba.budget_sub_activity = %s
				AND ba.source_of_fund = %s
				ORDER BY b.posting_date DESC, b.creation DESC
				LIMIT 1
			""", (
				cost_center,
				item.parent_account,
				item.account,
				item.budget_activity,
				item.budget_sub_activity,
				item.source_of_fund
			), as_dict=True)
			if not last_release:
				item.current_balance = flt(item.approved_budget) + flt(item.supplementary_budget) + flt(item.budget_received) - flt(item.budget_sent)
			else:
				last_budget_balance = flt(last_release[0].get("budget_balance") or 0.0)
				item.current_balance = last_budget_balance + flt(item.supplementary_budget) + flt(item.budget_received) - flt(item.budget_sent)
			item.budget_balance = flt(item.current_balance) - flt(item.released_budget)
			
			# if flt(item.released_budget) > flt(item.current_balance):
			# 	excess = flt(item.released_budget) - flt(item.current_balance)
			# 	frappe.throw(_(
			# 		"Released budget for Account {0}, Budget Activity {1}, Budget Sub Activity {2}, "
			# 		"Source of Fund {3} remaining budget of Nu. {4} and exceeds by Nu. {5}"
			# 	).format(
			# 		item.account,
			# 		item.budget_activity,
			# 		item.budget_sub_activity,
			# 		item.source_of_fund,
			# 		flt(item.current_balance),
			# 		excess
			# 	))

		self.approved_budget = approved_budget
		self.actual_total = total_actual
		self.supp_total = total_supplementary
		self.released_budget = released_budget
		self.budget_balance = sum([flt(d.budget_balance) for d in self.accounts])
		prev_release = frappe.db.sql("""
			SELECT b.budget_balance
			FROM `tabBudget Release` b
			WHERE b.docstatus = 1
			AND b.cost_center = %s
			ORDER BY b.posting_date DESC, b.creation DESC
			LIMIT 1
		""", (self.cost_center,), as_dict=True)

		if not prev_release:
			self.current_balance = flt(self.approved_budget)
		else:
			last_budget_balance = flt(prev_release[0].get("budget_balance") or 0.0)
			self.current_balance = last_budget_balance
		self.budget_balance = flt(self.current_balance) - flt(self.released_budget)






	# @frappe.whitelist()
	# def get_accounts(self):
	# 	condition = " and a.budget_type = '{}'".format(self.budget_type) if self.budget_type else ""
	# 	entries = frappe.db.sql("""select parent_account, a.name as account, a.budget_type, account_number
	# 						from tabAccount a
	# 						where a.is_group = 0
	# 						and (a.freeze_account is null or a.freeze_account != 'Yes')
	# 						and (a.is_centralized_budget = 0 or (a.is_centralized_budget =1 and a.cost_center='{cost_center}'))
	# 						and NOT EXISTS( select 1
	# 							from `tabBudget` b 
	# 							inner join `tabBudget Account` i
	# 							on b.name = i.parent
	# 							where  b.docstatus != 2
	# 							and i.account = a.name
	# 							and b.cost_center = '{cost_center}'
	# 							and b.fiscal_year = '{fiscal_year}'
	# 							and b.name != '{name}'
	# 						)
	# 						and EXISTS(select 1 
	# 											from `tabBudget Settings Account Types` s
	# 											where s.parent = 'Budget Settings'
	# 											and s.account_type = a.account_type)
	# 						{condition}
	# 					""".format(fiscal_year =self.fiscal_year, cost_center=self.cost_center, name=self.name, condition = condition), as_dict=True)
	# 	self.set('accounts', [])
	# 	p_account = ""
	# 	for d in entries:
	# 		d.initial_budget = 0
	# 		if d.parent_account == p_account:
	# 			d.parent_account = ""
	# 		else:
	# 			p_account = d.parent_account
	# 		row = self.append('accounts', {})
	# 		row.update(d)

	@frappe.whitelist()
	def get_accounts(self):
		"""Fetch account data from Budget where fiscal_year and cost_center match"""
		condition = " and a.budget_type = '{}'".format(self.budget_type) if self.budget_type else ""
		
		entries = frappe.db.sql("""
			select 
				a.parent_account as broad_head,
				a.name as account,
				a.parent_account,
				a.budget_type,
				a.account_number,
				ba.budget_amount as approved_budget,
				ba.released_budget,
				ba.budget_activity,
				ba.budget_sub_activity,
				ba.source_of_fund,
				ba.budget_activity_name,
				ba.budget_sub_activity_name,
				ba.source_of_fund_name,
				ba.account_name,
				b.cost_center,
				b.name as budget_id,
				b.fiscal_year
			from `tabAccount` a
			inner join `tabBudget Account` ba on ba.account = a.name
			inner join `tabBudget` b on b.name = ba.parent
			where 
				a.is_group = 0
				and (a.freeze_account is null or a.freeze_account != 'Yes')
				and b.docstatus = 1  -- Submitted budgets only
				and b.fiscal_year = %(fiscal_year)s
				and b.cost_center = %(cost_center)s
				and (a.is_centralized_budget = 0 or (a.is_centralized_budget = 1 and a.cost_center = %(cost_center)s))
				and EXISTS(select 1 
					from `tabBudget Settings Account Types` s
					where s.parent = 'Budget Settings'
					and s.account_type = a.account_type)
				{condition}
			GROUP BY a.name, ba.budget_activity, ba.budget_sub_activity, ba.source_of_fund
		""".format(condition=condition), {
			"fiscal_year": self.fiscal_year,
			"cost_center": self.cost_center
		}, as_dict=True)
		
		self.set('accounts', [])
		
		if not entries:
			frappe.msgprint(_("No accounts found with budget for Fiscal Year {0} and Cost Center {1}").format(
				self.fiscal_year, self.cost_center
			), indicator="orange")
			return
		
		p_account = ""
		for d in entries:
			# Set all required fields
			d.broad_head = d.get("broad_head")  # Already set from parent_account
			d.approved_budget = flt(d.get("approved_budget") or 0)
			d.released_budget = flt(d.get("released_budget") or 0)
			d.budget_amount = flt(d.get("approved_budget") or 0)
			d.initial_budget = flt(d.get("approved_budget") or 0)
			d.supplementary_budget = 0
			d.budget_received = 0
			d.budget_sent = 0
			d.current_balance = flt(d.get("approved_budget") or 0)
			d.budget_balance = flt(d.get("approved_budget") or 0) - flt(d.get("released_budget") or 0)
			
			# For display purposes
			if d.parent_account == p_account:
				d.parent_account = ""
			else:
				p_account = d.parent_account
				
			row = self.append('accounts', {})
			row.update(d)
		
		frappe.msgprint(_("{0} account(s) loaded from budget").format(len(entries)), indicator="green")
	
def delete_committed_consumed_budget(reference=None, reference_no=None):
	if reference and reference_no:
		frappe.db.sql("""Delete from `tabCommitted Budget` 
						where reference_type='{reference_type}' 
						and reference_no='{reference_no}'
						""".format(reference_type=reference, reference_no=reference_no))
		frappe.db.sql("""Delete from `tabConsumed Budget` 
						where reference_type='{reference_type}' 
						and reference_no='{reference_no}'
						""".format(reference_type=reference, reference_no=reference_no))



def validate_budget_records(args, error, budget_records, throw_error):
	for budget in budget_records:
		amount = get_amount(args, budget)
		yearly_action, monthly_action = get_actions(args, budget)
		monthly_budget_check = frappe.db.get_single_value("Budget Settings","monthly_budget_check")
		if monthly_budget_check:
			budget_account = args.expense_account
			if not budget_account:
				budget_account = args.account
			transaction_date = args.posting_date
			budget_amount = get_accumulated_monthly_budget(
				args.cost_center, budget_account, transaction_date, args.amount, args.fiscal_year
			)
			args["month_end_date"] = get_last_day(args.posting_date)
			compare_expense_with_budget(
				args, error, budget_amount, _("Accumulated Monthly"), monthly_action, budget.budget_against, amount, throw_error
			)
		else:
			budget_amount = budget.budget_amount
			if yearly_action in ("Stop", "Warn"):
				compare_expense_with_budget(
					args, error, flt(budget.budget_amount), _("Annual"), yearly_action, budget.budget_against, amount, throw_error
				)

def compare_expense_with_budget(args, error, budget_amount, action_for, action, budget_against, amount=0, throw_error=None):
	actual_expense = amount or args.amount
	if args.project:
		condition = " and cb.project = '{}'".format(budget_against)
	else:
		condition = " and cb.cost_center = {}".format(frappe.db.escape(budget_against))
		condition += " and cb.budget_activity = {}".format(frappe.db.escape(args.budget_activity))
		condition += " and cb.budget_sub_activity = {}".format(frappe.db.escape(args.budget_sub_activity))
		condition += " and cb.source_of_fund = {}".format(frappe.db.escape(args.source_of_fund))
	args.fiscal_year = args.fiscal_year if args.fiscal_year else str(args.posting_date)[0:4]
	start_date = get_first_day(args.posting_date)
	end_date = get_last_day(args.posting_date)
	committed = frappe.db.sql("""select SUM(cb.amount) as total 
								from `tabCommitted Budget` cb 
								where cb.account={account} 
								{condition} 
								and cb.reference_date between '{start_date}' and '{end_date}'""".format(condition=condition, 
							account=frappe.db.escape(args.account), cost_center=args.cost_center, start_date=start_date, 
							end_date=end_date), as_dict=True)
	consumed = frappe.db.sql("""select SUM(cb.amount) as total 
								from `tabConsumed Budget` cb 
								where cb.account={account}
								{condition} 
								and cb.reference_date between '{start_date}' and '{end_date}'""".format(condition=condition, 
							account=frappe.db.escape(args.account), cost_center=args.cost_center, start_date=start_date, 
							end_date=end_date), as_dict=True)
	if consumed and committed:
		if flt(consumed[0].total) > flt(committed[0].total):
			committed = consumed
		total_expense_amount = flt(committed[0].total) + flt(actual_expense)
		if frappe.db.get_single_value("Budget Settings","allow_budget_deviation"):
			deviation_percent = frappe.db.get_single_value("Budget Settings","deviation")
			if deviation_percent > 0:
				budget_amount = budget_amount  + (deviation_percent*budget_amount)/100
		available_budget = 	flt(budget_amount) - flt(committed[0].total)
	else:
		available_budget = flt(budget_amount)
		total_expense_amount = flt(actual_expense)

	if total_expense_amount > budget_amount:
		diff = total_expense_amount - budget_amount
		currency = frappe.get_cached_value("Company", args.company, "default_currency")
		message = ''
		if args.doctype in ("Purchase Order", "Purchase Invoice"):
			message = f" until #Row. {args.idx} with Item Code #{args.item_code}."

		msg = _("{0} Budget for Account {1} against {2} {3} for Budget Activity {8} and Budget Sub Activity {9} is {4} and available budget is {5} Including (Supplementary Budget,Budget Received,Budget Sent). It exceed by {6}{7}").format(
			_(action_for),
			frappe.bold(args.account),
			args.budget_against_field,
			frappe.bold(budget_against),
			frappe.bold(fmt_money(budget_amount, currency=currency)),
			frappe.bold(fmt_money(available_budget, currency=currency)),
			frappe.bold(fmt_money(diff, currency=currency)),
			message,
			frappe.bold(args.budget_activity),
			frappe.bold(args.budget_sub_activity),
		)

		if (
			frappe.flags.exception_approver_role
			and frappe.flags.exception_approver_role in frappe.get_roles(frappe.session.user)
		):
			action = "Warn"
		
		error.append(msg)
		if throw_error:
			if action == "Stop":
				frappe.msgprint(msg, raise_exception=True)
				frappe.throw(str(msg))
			else:
				frappe.msgprint(msg, indicator="orange")
				frappe.throw(str(msg))
		else:
			return error[0]

def commit_budget(args):
	amount = args.amount if args.amount else args.debit
	if frappe.db.get_single_value("Budget Settings", "budget_commit_on") == args.doctype and args.amount > 0:
		account_types = [d.account_type for d in frappe.get_all("Budget Settings Account Types", fields='account_type')]
		if frappe.db.get_value("Account", args.account, "account_type") in account_types:
			doc = frappe.get_doc(
				{
					"doctype": "Committed Budget",
					"account": args.account,
					"cost_center": args.cost_center,
					"committed_cost_center": args.committed_cost_center,
					"project": args.project,
					"reference_type": args.doctype,
					"reference_no": args.parent,
					"reference_date": args.posting_date,
					"reference_id": args.name,
					"amount": flt(amount,2),
					"item_code": args.item_code,
					"company": args.company
				}
			)
			doc.submit()

def get_actions(args, budget):
	yearly_action = budget.action_if_annual_budget_exceeded
	monthly_action = budget.action_if_accumulated_monthly_budget_exceeded

	if args.get("doctype") == "Material Request" and budget.for_material_request:
		yearly_action = budget.action_if_annual_budget_exceeded_on_mr
		monthly_action = budget.action_if_accumulated_monthly_budget_exceeded_on_mr

	elif args.get("doctype") == "Purchase Order" and budget.for_purchase_order:
		yearly_action = budget.action_if_annual_budget_exceeded_on_po
		monthly_action = budget.action_if_accumulated_monthly_budget_exceeded_on_po

	return yearly_action, monthly_action


def get_amount(args, budget):
	amount = 0
	if args.amount:
		amount = args.amount
	else:
		amount = args.debit
	return amount


def get_requested_amount(args, budget):
	item_code = args.get("item_code")
	condition = get_other_condition(args, budget, "Material Request")

	data = frappe.db.sql(
		""" select ifnull((sum(child.stock_qty - child.ordered_qty) * rate), 0) as amount
		from `tabMaterial Request Item` child, `tabMaterial Request` parent where parent.name = child.parent and
		child.item_code = %s and parent.docstatus = 1 and child.stock_qty > child.ordered_qty and {0} and
		parent.material_request_type = 'Purchase' and parent.status != 'Stopped'""".format(
			condition
		),
		item_code,
		as_list=1,
	)

	return data[0][0] if data else 0


def get_ordered_amount(args, budget):
	item_code = args.get("item_code")
	condition = get_other_condition(args, budget, "Purchase Order")

	data = frappe.db.sql(
		""" select ifnull(sum(child.amount - child.billed_amt), 0) as amount
		from `tabPurchase Order Item` child, `tabPurchase Order` parent where
		parent.name = child.parent and child.item_code = %s and parent.docstatus = 1 and child.amount > child.billed_amt
		and parent.status != 'Closed' and {0}""".format(
			condition
		),
		item_code,
		as_list=1,
	)

	return data[0][0] if data else 0


def get_other_condition(args, budget, for_doc):
	condition = "expense_account = '%s'" % (args.expense_account)
	budget_against_field = args.get("budget_against_field")

	if budget_against_field and args.get(budget_against_field):
		condition += " and child.%s = '%s'" % (budget_against_field, args.get(budget_against_field))

	if args.get("fiscal_year"):
		date_field = "schedule_date" if for_doc == "Material Request" else "transaction_date"
		start_date, end_date = frappe.db.get_value(
			"Fiscal Year", args.get("fiscal_year"), ["year_start_date", "year_end_date"]
		)

		condition += """ and parent.%s
			between '%s' and '%s' """ % (
			date_field,
			start_date,
			end_date,
		)

	return condition


def get_actual_expense(args):
	if not args.budget_against_doctype:
		args.budget_against_doctype = frappe.unscrub(args.budget_against_field)

	budget_against_field = args.get("budget_against_field")
	condition1 = " and gle.posting_date <= %(month_end_date)s" if args.get("month_end_date") else ""

	if args.is_tree:
		lft_rgt = frappe.db.get_value(
			args.budget_against_doctype, args.get(budget_against_field), ["lft", "rgt"], as_dict=1
		)

		args.update(lft_rgt)

		condition2 = """and exists(select name from `tab{doctype}`
			where lft>=%(lft)s and rgt<=%(rgt)s
			and name=gle.{budget_against_field})""".format(
			doctype=args.budget_against_doctype, budget_against_field=budget_against_field  # nosec
		)
	else:
		condition2 = """and exists(select name from `tab{doctype}`
		where name=gle.{budget_against} and
		gle.{budget_against} = %({budget_against})s)""".format(
			doctype=args.budget_against_doctype, budget_against=budget_against_field
		)

	amount = flt(
		frappe.db.sql(
			"""
		select sum(gle.debit) - sum(gle.credit)
		from `tabGL Entry` gle
		where gle.account=%(account)s
			{condition1}
			and gle.fiscal_year=%(fiscal_year)s
			and gle.company=%(company)s
			and gle.docstatus=1
			{condition2}
	""".format(
				condition1=condition1, condition2=condition2
			),
			(args),
		)[0][0]
	)  # nosec

	return amount

from datetime import datetime
def get_accumulated_monthly_budget(cost_center, budget_account, transaction_date, amount, fiscal_year):
	# mydate = datetime.strptime(transaction_date, '%Y-%m-%d')
	mydate = datetime.fromisoformat(str(transaction_date))
	month = mydate.month
	if frappe.db.get_value("Account", budget_account, "ignore_budget_check"):
		return
	budget_against = frappe.db.get_single_value("Budget Settings","budget_against")
	cond = ""
	if budget_against == "Cost Center":
		cond += ''' and b.budget_against = "{}" and b.cost_center = "{}" '''.format(budget_against, cost_center)
	else:
		cond += ''' and b.budget_against = "{}" '''.format(budget_against)
	budget_amount = frappe.db.sql('''select b.action_if_annual_budget_exceeded as annual_action, ba.budget_check,\
					ba.budget_amount, b.deviation, \
					ba.january, ba.february, ba.march, ba.april, ba.may, ba.june, ba.july, ba.august, ba.september, ba.october, ba.november, ba.december\
					from `tabBudget` b, `tabBudget Account` ba \
					where b.docstatus = 1 \
					and ba.parent = b.name and ba.account= "{}" \
					and b.fiscal_year = "{}" {} '''.format(budget_account, str(transaction_date)[0:4], cond), as_dict=True)
	# frappe.throw(str(budget_amount))
	if month == 1:
		monthly_amount = budget_amount[0].january
		month_name = "January"
	elif month == 2:
		monthly_amount = budget_amount[0].february
		month_name = "February"
	elif month == 3:
		monthly_amount = budget_amount[0].march
		month_name = "March"
	elif month == 4:
		monthly_amount = budget_amount[0].april
		month_name = "April"
	elif month == 5:
		monthly_amount = budget_amount[0].may
		month_name = "May"
	elif month == 6:
		monthly_amount = budget_amount[0].june
		month_name = "June"
	elif month == 7:
		monthly_amount = budget_amount[0].july
		month_name = "July"
	elif month == 8:
		monthly_amount = budget_amount[0].august
		month_name = "August"
	elif month == 9:
		monthly_amount = budget_amount[0].september
		month_name = "September"
	elif month == 10:
		monthly_amount = budget_amount[0].october
		month_name = "October"
	elif month == 11:
		monthly_amount = budget_amount[0].november
		month_name = "November"
	else:
		monthly_amount = budget_amount[0].december
		month_name = "December"

	if transaction_date:
		month_first_date = get_first_day(transaction_date)
		month_last_date = get_last_day(transaction_date)
		supplement = flt(frappe.db.sql("""
				select sum(amount)
				from `tabSupplementary Details`
				where month = "{month}"
				and fiscal_year = "{fiscal_year}"
				and account="{account}"
				and cost_center="{cost_center}"
			""".format(from_date=month_first_date, to_date=month_last_date,account = budget_account, month = month_name, cost_center=cost_center, fiscal_year=fiscal_year))[0][0],2)
		monthly_received = frappe.db.sql("""
				select sum(amount)
				from `tabReappropriation Details`
				where fiscal_year = "{fiscal_year}"
				and to_account="{account}"
				and to_cost_center="{cost_center}"
				and to_month = "{month}"
			""".format(from_date=month_first_date, to_date=month_last_date, month = month_name, account = budget_account, cost_center=cost_center, fiscal_year=fiscal_year))[0][0]
		monthly_sent = frappe.db.sql("""
				select sum(amount)
				from `tabReappropriation Details`
				where fiscal_year = "{fiscal_year}"
				and from_account="{account}"
				and from_cost_center="{cost_center}"
				and from_month = "{month}"
			""".format(from_date=month_first_date, to_date=month_last_date,month = month_name, account = budget_account, cost_center=cost_center, fiscal_year=fiscal_year))[0][0]
		adjustment = flt(supplement,2) + flt(monthly_received,2) - flt(monthly_sent,2)
	if adjustment:
		sum =flt(adjustment) + flt(monthly_amount)
		return sum
	else:
		return monthly_amount


def get_item_details(args):
	cost_center, expense_account = None, None

	if not args.get("company"):
		return cost_center, expense_account

	if args.item_code:
		item_defaults = frappe.db.get_value(
			"Item Default",
			{"parent": args.item_code, "company": args.get("company")},
			["buying_cost_center", "expense_account"],
		)
		if item_defaults:
			cost_center, expense_account = item_defaults

	if not (cost_center and expense_account):
		for doctype in ["Item Group", "Company"]:
			data = get_expense_cost_center(doctype, args)

			if not cost_center and data:
				cost_center = data[0]

			if not expense_account and data:
				expense_account = data[1]

			if cost_center and expense_account:
				return cost_center, expense_account

	return cost_center, expense_account


def get_expense_cost_center(doctype, args):
	if doctype == "Item Group":
		return frappe.db.get_value(
			"Item Default",
			{"parent": args.get(frappe.scrub(doctype)), "company": args.get("company")},
			["buying_cost_center", "expense_account"],
		)
	else:
		return frappe.db.get_value(
			doctype, args.get(frappe.scrub(doctype)), ["cost_center", "default_expense_account"]
		)

def get_permission_query_conditions(user=None):
    if not user:
        user = frappe.session.user

    roles = frappe.get_roles(user)

    if "System Manager" in roles:
        return ""

    if "Accounts User" in roles:
        return f"""
            `tabBudget Release`.owner = {frappe.db.escape(user)}
            AND `tabBudget Release`.workflow_state  IN('Draft','Waiting for MOF Finance Approval','Waiting Accounts Verification','Approved','Rejected')
        """

    if "Accounts Manager" in roles:
        return """
            `tabBudget Proposal`.workflow_state IN('Waiting Accounts Verification','Approved','Rejected')
        """
    if "Budget Approver" in roles:
        return """
            `tabBudget Release`.workflow_state IN('Waiting for MOF Finance Approval','Approved','Rejected')
        """

    return "1=0"