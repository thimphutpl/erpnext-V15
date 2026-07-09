# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint, scrub
from frappe.model.document import Document
from frappe.utils import cint, cstr, flt, fmt_money, formatdate, get_link_to_form, nowdate
# from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states

class WithdrawalBudget(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.withdrawal_budget_item.withdrawal_budget_item import WithdrawalBudgetItem
		from frappe.types import DF

		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Data | None
		approver_name: DF.Data | None
		attachment: DF.Attach | None
		budget_against: DF.Literal["", "Cost Center", "Project"]
		company: DF.Link
		cost_center: DF.Link | None
		fiscal_year: DF.Link
		items: DF.Table[WithdrawalBudgetItem]
		posting_date: DF.Date
		project: DF.Link | None
		remarks: DF.SmallText | None
	# end: auto-generated types

	
	def validate(self):
		# validate_workflow_states(self)
		self.validate_budget()
		self.set_broad_head_from_account()
		# if self.workflow_state != "Submitted":
		# 	notify_workflow_states(self)

	def on_submit(self):
		# notify_workflow_states(self)
		self.withdrawal_budget(cancel=False)

	def on_cancel(self):
		self.withdrawal_budget(cancel=True)
		# notify_workflow_states(self)

	def set_broad_head_from_account(self):
		"""Auto-set broad_head as parent_account of selected account"""
		for row in self.get("items"):  # Replace with your child table fieldname
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

	#Added by Thukten on 13th Sept, 2023
	def validate_budget(self):
		budget_against_field = frappe.scrub(self.budget_against)
		budget_against = self.get(budget_against_field)
		if not self.items:
			frappe.throw(_("Please provide Budget Head or Account to supplement budget"))

		for d in self.items:
			query = """
				SELECT
					b.name, ba.account 
				FROM `tabBudget` b, `tabBudget Account` ba
				WHERE
					ba.parent = b.name 
					AND b.docstatus = 1 
					AND b.company = %s 
					AND b.{0} = %s 
					AND b.fiscal_year = %s 
					AND ba.account = %s
			""".format(budget_against_field)
			
			params = [self.company, budget_against, self.fiscal_year, d.account]

			if d.get('budget_activity'):
				query += " AND ba.budget_activity = %s"
				params.append(d.budget_activity)

			if d.get('budget_sub_activity'):
				query += " AND ba.budget_sub_activity = %s"
				params.append(d.budget_sub_activity)

			budget_exist = frappe.db.sql(query, params, as_dict=1)
			
			if not budget_exist:
				error_message = _(
					"Budget record does not exist against {0} '{1}' and account '{2}' for fiscal year {3}"
				).format(self.budget_against, budget_against, d.account, self.fiscal_year)
				if d.get('budget_activity'):
					error_message += _(" with budget activity '{0}'").format(d.budget_activity)
				if d.get('budget_sub_activity'):
					error_message += _(" and budget sub-activity '{0}'").format(d.budget_sub_activity)
				
				frappe.throw(error_message)

	# Written by Thukten to perform budget supplement, 13 Sept 2022
	def withdrawal_budget(self, cancel=False):
		if frappe.db.get_value("Fiscal Year", self.fiscal_year, "closed"):
			frappe.throw(_("Fiscal Year {0} has already been closed").format(self.fiscal_year))
		else:
			budget_against_field = frappe.scrub(self.budget_against)
			budget_against = self.get(budget_against_field)
			for d in self.items:
				month = d.month
				if d.amount <= 0:
					frappe.throw(_("Budget Withdrawal Amount should be greater than 0 for record {0}").format(d.idx))
				query = """
					SELECT
						ba.name, ba.account
					FROM
						`tabBudget` b, `tabBudget Account` ba
					WHERE
						ba.parent = b.name
						AND b.docstatus < 2
						AND b.company = %s
						AND b.{0} = %s 
						AND b.fiscal_year = %s
						AND ba.account = %s
				""".format(budget_against_field)
				
				params = [self.company, budget_against, self.fiscal_year, d.account]
				
				if d.get('budget_activity'):
					query += " AND ba.budget_activity = %s"
					params.append(d.budget_activity)
				if d.get('budget_sub_activity'):
					query += " AND ba.budget_sub_activity = %s"
					params.append(d.budget_sub_activity)

				to_account = frappe.db.sql(query, params, as_dict=1)
				
				if to_account:
					to_budget_account = frappe.get_doc("Budget Account", to_account[0].name)
					if cancel:
						total = flt(to_budget_account.budget_amount) + flt(d.amount)
						sup_budget = flt(to_budget_account.withdrawal_budget) + flt(d.amount)
						frappe.db.sql("DELETE FROM `tabWithdrawal Details` WHERE reference = %s", self.name)
					else:
						sup_budget = flt(to_budget_account.withdrawal_budget) - flt(d.amount)
						total = flt(to_budget_account.budget_amount) - flt(d.amount)
						supp_details = frappe.new_doc("Withdrawal Details")
						supp_details.budget_against = self.budget_against
						supp_details.cost_center = self.cost_center if self.budget_against == "Cost Center" else ""
						supp_details.project = self.project if self.budget_against == "Project" else ""
						supp_details.account = d.account
						supp_details.budget_activity = d.get('budget_activity', '')
						supp_details.budget_sub_activity = d.get('budget_sub_activity', '')
						supp_details.amount = flt(d.amount)
						supp_details.company = self.company
						supp_details.month = month
						supp_details.reference = self.name
						supp_details.posting_date = nowdate()
						supp_details.fiscal_year = self.fiscal_year
						supp_details.insert(ignore_permissions=True)
					
					monthly_budget = frappe.db.get_single_value("Budget Settings", "monthly_budget_check")
					to_budget_account.db_set("withdrawal_budget", flt(sup_budget, 2))
					
					if monthly_budget:
						if month:
							month_field_map = {
								"January": "sb_january",
								"February": "sb_february",
								"March": "sb_march",
								"April": "sb_april",
								"May": "sb_may",
								"June": "sb_june",
								"July": "sb_july",
								"August": "sb_august",
								"September": "sb_september",
								"October": "sb_october",
								"November": "sb_november",
								"December": "sb_december"
							}
							
							if month in month_field_map:
								month_field = month_field_map[month]
								current_value = flt(getattr(to_budget_account, month_field, 0))
								if cancel:
									new_value = current_value - flt(d.amount)
								else:
									new_value = current_value + flt(d.amount)
								to_budget_account.db_set(month_field, flt(new_value))
							else:
								frappe.throw(_("Invalid month specified: {0}").format(month))
						else:
							frappe.throw(_("Please Enter Month"))
					
					to_budget_account.db_set("budget_amount", flt(total))
				else:
					error_message = _(
						"Budget not set for account {0} under {1} {2}. Please check initial budget allocations"
					).format(d.account, self.budget_against, budget_against)

					if d.get('budget_activity'):
						error_message += _(" with budget activity '{0}'").format(d.budget_activity)
					if d.get('budget_sub_activity'):
						error_message += _(" and budget sub-activity '{0}'").format(d.budget_sub_activity)
					
					frappe.throw(error_message)
