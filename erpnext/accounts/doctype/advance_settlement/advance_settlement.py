# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt,nowtime,nowdate
from frappe.utils import money_in_words
from erpnext.custom_utils import prepare_gl
from frappe import _
from erpnext.custom_utils import check_budget_available

class AdvanceSettlement(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.mobilisation_advance_item.mobilisation_advance_item import MobilisationAdvanceItem
		from erpnext.budget.doctype.advance_recoup_item.advance_recoup_item import AdvanceRecoupItem
		from frappe.types import DF

		adjustment_type: DF.Literal["", "Advance Settlement", "Recovery"]
		advance_list: DF.Table[MobilisationAdvanceItem]
		advance_type: DF.Link | None
		amended_from: DF.Link | None
		apply_retention: DF.Check
		apply_tds: DF.Check
		branch: DF.Link
		company: DF.Link | None
		cost_center: DF.Link | None
		customer: DF.DynamicLink | None
		expense_details: DF.Table[AdvanceRecoupItem]
		is_running_bill: DF.Check
		journal_entry: DF.Data | None
		mode_of_payment: DF.Link | None
		net_amount: DF.Currency
		party_type: DF.Literal["", "Customer", "Supplier", "Employee"]
		payment_status: DF.Data | None
		posting_date: DF.Date | None
		retention: DF.Link | None
		retention_account: DF.Data | None
		retention_amount: DF.Currency
		retention_rate: DF.Data | None
		tds: DF.Link | None
		tds_account: DF.Data | None
		tds_amount: DF.Currency
		tds_rate: DF.Data | None
	# end: auto-generated types

	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.mobilisation_advance_item.mobilisation_advance_item import MobilisationAdvanceItem
		from frappe.types import DF

		advance_list: DF.Table[MobilisationAdvanceItem]
		advance_type: DF.Link | None
		amended_from: DF.Link | None
		amount: DF.Currency
		branch: DF.Link | None
		company: DF.Link | None
		cost_center: DF.Link | None
		customer: DF.DynamicLink | None
		journal_entry: DF.Data | None
		party_type: DF.Literal["", "Customer", "Supplier", "Employee"]
		posting_date: DF.Date | None
		total_amount: DF.Currency
	def validate(self):
		self.calculate_advance_balance()
		self.calculate_tds()
		self.calculate_retention()
		self.calculate_net_amount()

	def before_cancel(self):
		if not self.journal_entry:
			return
		
		je = frappe.get_doc("Journal Entry", self.journal_entry)			
		if je.workflow_state in (
			"Waiting For Verification",
			"Waiting Approval",
		):
			frappe.throw(
				_(
					"Cannot cancel Advance {0} because linked Journal Entry {1}. "
					"Please Reject it first."
				).format(self.name, self.journal_entry)
		)
	def on_cancel(self):
		self.ignore_linked_doctypes = (
					"GL Entry",
					"Payment Ledger Entry",
				)
		self.return_advance_amount()
		self.removed_journal_entry()

	
		
	def on_submit(self):


		if self.is_running_bill:
			self.post_journal_entry()
			self.make_mobilisation_entry()
	
	
	def calculate_advance_balance(self):
		for item in self.advance_list:

			advance_amount = flt(item.advance_amount)
			allocated_amount = flt(item.allocated_amount)

			if allocated_amount > advance_amount:
				frappe.throw(
					_("Allocated Amount cannot be greater than Advance Amount for {0}").format(
						item.reference
					)
				)

			item.total_amount = advance_amount
			item.balance_amount = advance_amount - allocated_amount
	def get_expense_amount(self):
		total = 0

		for item in self.expense_details:
			total += flt(item.amount)

		return total
	def get_allocated_amount(self):
		total = 0

		for item in self.advance_list:
			total += flt(item.allocated_amount)

		return total

	def calculate_tds(self):
		if self.apply_tds and self.tds:
			expense_amount = self.get_expense_amount()
			self.tds_amount = expense_amount * flt(self.tds_rate) / 100
		else:
			self.tds_amount = 0


	def calculate_retention(self):
		if self.apply_retention and self.retention:
			expense_amount = self.get_expense_amount()
			self.retention_amount = expense_amount * flt(self.retention_rate) / 100
		else:
			self.retention_amount = 0
	# def calculate_net_amount(self):
	# 	allocated_amount = self.get_allocated_amount()
	# 	expense_amount = self.get_expense_amount()

	# 	self.net_amount = (expense_amount-
	# 		allocated_amount
	# 		- flt(self.tds_amount)
	# 		- flt(self.retention_amount)
	# 	)
	def calculate_net_amount(self):
		allocated_amount = flt(self.get_allocated_amount())
		expense_amount = flt(self.get_expense_amount())
		tds_amount = flt(self.tds_amount)
		retention_amount = flt(self.retention_amount)
		if expense_amount:
			if expense_amount <= allocated_amount:
				self.net_amount = (
					allocated_amount
					- expense_amount
					- tds_amount
					- retention_amount
				)
			else:
				self.net_amount = (
					expense_amount
					- allocated_amount
					- tds_amount
					- retention_amount
				)
		else:
			self.net_amount = 0
	
	def return_advance_amount(self):
		for item in self.advance_list:
			if not item.reference:
				continue

			advance_entry = frappe.db.get_value(
				"Advance Entry",
				{
					"advance": item.reference,
					"docstatus": 1
				},
				"name"
			)

			if not advance_entry:
				continue

			doc = frappe.get_doc("Advance Entry", advance_entry)

			for row in doc.mobilisation_entry:
				if row.reference != item.reference:
					continue

				deduction = flt(item.allocated_amount)

				row.allocated_amount = max(
					0,
					flt(row.allocated_amount) - deduction
				)

				row.balance_amount = (
					flt(row.advance_amount) - flt(row.allocated_amount)
				)

			doc.save(ignore_permissions=True)

	def removed_journal_entry(self):
		
		if not self.journal_entry:
			return

		je_name = self.journal_entry

		# Find linked Advance
		advance_name = frappe.db.get_value(
			"Advance",
			{"journal_entry": je_name},
			"name"
		)

		if advance_name:
			# Remove the Journal Entry link from Advance
			frappe.db.set_value(
				"Advance",
				advance_name,
				"journal_entry",
				None
			)

		# Delete Journal Entry if Draft
		if frappe.db.exists("Journal Entry", je_name):
			je = frappe.get_doc("Journal Entry", je_name)

			if je.workflow_state in ["Draft","Rejected","Cancelled"] and je.docstatus == 0:
				frappe.delete_doc(
					"Journal Entry",
					je_name,
					ignore_permissions=True
				)

			self.db_set("journal_entry", None)
	def make_mobilisation_entry(self, cancel=False):

		for acc in self.advance_list:

			con = frappe.get_doc("Advance Entry", acc.advance_entry)

			for row in con.mobilisation_entry:

				if row.reference == acc.reference:

					if cancel:
						row.allocated_amount -= flt(acc.allocated_amount)
					else:
						row.allocated_amount += flt(acc.allocated_amount)

					row.balance_amount = (
						flt(row.advance_amount)
						- flt(row.allocated_amount)
					)

					break

			con.flags.ignore_validate_update_after_submit = True
			con.save(ignore_permissions=True)
	
	
	

	
	def post_journal_entry(self):
		
		credit_account = frappe.db.get_value("Company", self.company, "default_bank_account")
		voucher_type=""
		naming_series=""
		if self.adjustment_type=="Recovery":
			voucher_type = "Other Voucher"
			naming_series = "Other Voucher"
		else:
			voucher_type = "Disbursement Voucher"
			naming_series = "Disbursement Voucher"
		prefix = frappe.db.get_value(
					"Journal Entry Series",
					naming_series,
					"name"
				)
		party_type = ""
		party = ""
		account_type = ""
		expense_account_type = ""
		credit_account_type = frappe.db.get_value("Account", credit_account, "account_type")
		tds_account = frappe.db.get_value("Account", self.tds_account, "account_type")
		retention_account = frappe.db.get_value("Account", self.retention_account, "account_type")

		for item in self.advance_list:
			advance_account = item.account

			account_type = frappe.db.get_value(
				"Account", advance_account, "account_type"
			)
		for i in self.expense_details:
			expense_account = i.account

			expense_account_type = frappe.db.get_value(
				"Account", expense_account, "account_type"
			)

		debit_account=None
		if self.mode_of_payment == "Cash":
			debit_account = frappe.db.get_value("Company", self.company, "default_cash_account")
		elif self.mode_of_payment == "Wire Transfer":
			debit_account = frappe.db.get_value("Company", self.company, "default_bank_account")
	
	
		
		
		if credit_account_type in ("Payable", "Receivable") or account_type in ("Payable", "Receivable") or tds_account in ("Payable", "Receivable") or retention_account in ("Payable", "Receivable")or expense_account_type in ("Payable", "Receivable"):
			party_type = self.party_type
			party = self.customer

		je = frappe.new_doc("Journal Entry")
		account=None
		broad_head=None
		budget_activity=None
		budget_sub_activity=None
		source_of_fund=None
		allocated_amount = self.get_allocated_amount()
		expense_amount = self.get_expense_amount()
		je.voucher_type=voucher_type
		je.title=self.name
		je.naming_series=prefix
		je.posting_date=self.posting_date
		je.company=self.company
		je.branch=self.branch
		je.total_amount_in_words= money_in_words(self.net_amount),
		je.reference_doctype=self.doctype
		je.reference_link=self.name

	
		# if self.adjustment_type=="Advance Settlement":
			# for i in self.advance_list:
			# 	allocated_amount = flt(i.allocated_amount)
			# 	if allocated_amount > 0:
			# 		je.append("accounts", {
			# 			"account": i.account,
			# 			"reference_type": self.doctype,
			# 			"reference_name": self.name,
			# 			"cost_center": self.cost_center,
			# 			"credit_in_account_currency": allocated_amount,
			# 			"credit": allocated_amount,
			# 			"party_type": party_type,
			# 			"party": party,
			# 			"budget_activity": i.budget_activity,
			# 			"budget_sub_activity": i.budget_sub_activity,
			# 			"source_of_fund": i.source_of_fund
			# 		})

			# for item in self.expense_details:
			# 	expense_amount = flt(item.amount)

			# 	if expense_amount > 0:
			# 		je.append("accounts", {
			# 			"account": item.account,
			# 			"reference_type": self.doctype,
			# 			"reference_name": self.name,
			# 			"cost_center": self.cost_center,
			# 			"debit_in_account_currency": expense_amount,
			# 			"debit": expense_amount,
			# 			"broad_head": item.broad_head,
			# 			"party_type": party_type,
			# 			"party": party,
			# 			"budget_activity": item.budget_activity,
			# 			"budget_sub_activity": item.budget_sub_activity,
			# 			"source_of_fund": item.source_of_fund
			# 		})
		if self.adjustment_type=="Recovery":
			for i in self.advance_list:
				allocated_amount = flt(i.allocated_amount)

				if allocated_amount > 0:
					je.append("accounts", {
						"account": i.account,
						"reference_type": self.doctype,
						"reference_name": self.name,
						"cost_center": self.cost_center,
						"credit_in_account_currency": allocated_amount,
						"credit": allocated_amount,
						"party_type": party_type,
						"party": party,
						"budget_activity": i.budget_activity,
						"budget_sub_activity": i.budget_sub_activity,
						"source_of_fund": i.source_of_fund
					})
					je.append("accounts", {
						"account": debit_account,
						"reference_type": self.doctype,
						"reference_name": self.name,
						"cost_center": self.cost_center,
						"debit_in_account_currency": allocated_amount,
						"debit": allocated_amount,
						"budget_activity": item.budget_activity,
						"budget_sub_activity": item.budget_sub_activity,
						"source_of_fund": item.source_of_fund
					})

					
		elif self.adjustment_type=="Advance Settlement":
			for item in self.expense_details:
				account=item.account
				broad_head = item.broad_head
				budget_activity = item.budget_activity
				budget_sub_activity = item.budget_sub_activity
				source_of_fund = item.source_of_fund

			for i in self.advance_list:
				je.append("accounts", {
						"account": i.account,
						"reference_type": self.doctype,
						"reference_name": self.name,
						"cost_center": self.cost_center,
						"credit_in_account_currency": flt(i.allocated_amount),
						"credit": flt(i.allocated_amount),
						"party_type": party_type,
						"party": party,
						"budget_activity": i.budget_activity,
						"budget_sub_activity": i.budget_sub_activity,
						"source_of_fund": i.source_of_fund
		
					})
				
			if self.net_amount > 0:
				je.append("accounts", {
						"account": account,
						"reference_type": self.doctype,
						"reference_name": self.name,
						"cost_center": self.cost_center,
						"debit_in_account_currency": flt(expense_amount),
						"debit": flt(expense_amount),
						"broad_head": broad_head,
						"budget_activity": budget_activity,
						"budget_sub_activity": budget_sub_activity,
						"source_of_fund": source_of_fund,
						"party_type": party_type,
						"party": party

						})
				je.append("accounts", {
					"account": credit_account,
					"reference_type":self.doctype,
					"reference_name": self.name,
					"cost_center": self.cost_center,
					"credit_in_account_currency": flt(self.net_amount),
					"credit": flt(self.net_amount),
					"budget_activity": budget_activity,
					"budget_sub_activity": budget_sub_activity,
					"source_of_fund": source_of_fund

				})
			else:
				for item in self.expense_details:
					amount = flt(item.amount)
					if allocated_amount > 0:
						je.append("accounts", {
							"account": item.account,
							"reference_type": self.doctype,
							"reference_name": self.name,
							"cost_center": self.cost_center,
							"debit_in_account_currency": amount,
							"debit": amount,
							"party_type": party_type,
							"party": party,
							"broad_head": broad_head,
							"budget_activity": budget_activity,
							"budget_sub_activity":budget_sub_activity,
							"source_of_fund": source_of_fund

						})
			

			if self.tds_amount > 0 :
				je.append("accounts", {
				"account": self.tds_account,
				"reference_type": self.doctype,
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.tds_amount),
				"credit": flt(self.tds_amount),
				"party_type": self.party_type,
				"party": party,
				"ignore_budget_details":1
			})
			if self.retention_amount > 0:
				je.append("accounts", {
				"account": self.retention_account,
				"reference_type":self.doctype,
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.retention_amount),
				"credit": flt(self.retention_amount),
				"party_type": self.party_type,
				"party": party,
				"ignore_budget_details":1
			})
		je.insert()
		# frappe.db.commit()		
		self.db_set("journal_entry", je.name)
		frappe.msgprint("Journal Entry created. {}".format(frappe.get_desk_link("Journal Entry", je.name)))

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles or "Accounts User" in user_roles or "Accounts Manager" in user_roles: 
		return

	return """(
		exists(select 1
			from `tabEmployee` as e
			where e.branch = `tabAdvance Settlement`.branch
			and e.user_id = '{user}')
	)""".format(user=user)
	