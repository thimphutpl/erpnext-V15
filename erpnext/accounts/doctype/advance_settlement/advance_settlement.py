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
		net_amount: DF.Currency
		party_type: DF.Literal["", "Customer", "Supplier", "Employee"]
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
		# self.calculate_advance_balance()
		self.calculate_tds()
		self.calculate_retention()
		self.calculate_net_amount()
	# 	if self.docstatus==0:
	# 		self.calculate_amount()
		# self.check_budget_availability()
	
		
	def on_submit(self):
		self.calculate_advance_balance()

		if self.is_running_bill:
			self.update_general_ledger()
			self.post_journal_entry()
			self.make_mobilisation_entry()
    
	




	def calculate_advance_balance(self):
		for item in self.advance_list:
			# if item.allocated_amount > 0:
			if flt(item.allocated_amount) > flt(item.total_amount):
				frappe.throw(
					_("Allocated Amount cannot be greater than Balance Amount for {0}").format(item.reference)
				)
			item.balance_amount = (
				flt(item.total_amount)
				- flt(item.allocated_amount)
			)
			item.total_amount = flt(item.balance_amount)
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
	def calculate_net_amount(self):
		allocated_amount = self.get_allocated_amount()
		expense_amount = self.get_expense_amount()

		self.net_amount = (expense_amount-
			allocated_amount
			- flt(self.tds_amount)
			- flt(self.retention_amount)
		)
	



	

	def make_mobilisation_entry(self, cancel=False):
		frappe.db.sql("""
			UPDATE `tabAdvance Entry`
			SET is_running_bill = 0
			WHERE customer = %s AND branch = %s AND is_running_bill = 1
		""", (self.customer, self.branch))
		if self.is_running_bill:
			con = frappe.new_doc("Advance Entry")
			con.branch = self.branch
			con.posting_date = self.posting_date
			con.posting_time = nowtime()
			con.customer = self.customer
			con.branch = self.branch
			con.reference_type = 'Advance Entry'
			con.is_running_bill = self.is_running_bill
			con.advance_settlement = self.name
			con.party_type= self.party_type
			for acc in self.advance_list:
				con.append("mobilisation_entry", {
					"reference":acc.reference,
					"advance_type": acc.advance_type,
					"allocated_amount": acc.allocated_amount,
					"total_amount": acc.balance_amount,
					"balance_amount": acc.balance_amount,
					"advance_amount": acc.advance_amount
				})
			con.insert(ignore_permissions=True)
			con.submit()
	
	
	

	def update_general_ledger(self):
		gl_entries = []
		broad_head=None
		budget_activity=None
		budget_sub_activity=None
		source_of_fund=None
		account=None
		

		credit_account = frappe.db.get_value("Advance Type", self.advance_type, "advance_account")
		allocated_amount = self.get_allocated_amount()
		expense_amount = self.get_expense_amount()

		for item in self.expense_details:
			account=item.account
			broad_head=item.broad_head
			budget_activity = item.budget_activity
			budget_sub_activity = item.budget_sub_activity
			source_of_fund = item.source_of_fund

		if not credit_account:
			frappe.throw("Please set Default Bank Account in Company")
	
		gl_entries.append(
			prepare_gl(self, {
				"account": account,
				"reference_type": "Advance Settlement",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"debit_in_account_currency": flt(expense_amount),
				"debit": flt(expense_amount),
				"broad_head": broad_head,
				"budget_activity":budget_activity,
				"budget_sub_activity": budget_sub_activity,
				"source_of_fund": source_of_fund
				
			})
		)
		gl_entries.append(
			prepare_gl(self, {
				"account":credit_account,
				"reference_type": "Advance Settlement",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(allocated_amount),
				"credit": flt(allocated_amount),
				"broad_head": broad_head,
				"budget_activity":budget_activity,
				"budget_sub_activity": budget_sub_activity,
				"source_of_fund": source_of_fund
				
			})
		)
		gl_entries.append(
			prepare_gl(self, {
				"account":credit_account,
				"reference_type": "Advance Settlement",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.net_amount),
				"credit": flt(self.net_amount),
				"broad_head": broad_head,
				"budget_activity":budget_activity,
				"budget_sub_activity": budget_sub_activity,
				"source_of_fund": source_of_fund
				
			})
		)
		gl_entries.append(
			prepare_gl(self, {
				"account":self.tds_account,
				"reference_type": "Advance Settlement",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.tds_amount),
				"credit": flt(self.tds_amount),
				"broad_head": broad_head,
				"budget_activity":budget_activity,
				"budget_sub_activity": budget_sub_activity,
				"source_of_fund": source_of_fund
				
			})
		)
		gl_entries.append(
			prepare_gl(self, {
				"account":self.retention_account,
				"reference_type": "Advance Settlement",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.retention_amount),
				"credit": flt(self.retention_amount),
				"broad_head": broad_head,
				"budget_activity":budget_activity,
				"budget_sub_activity": budget_sub_activity,
				"source_of_fund": source_of_fund
				
			})
		)



		
		
	
	
		if gl_entries:
			from erpnext.accounts.general_ledger import make_gl_entries
			make_gl_entries(gl_entries, cancel=(self.docstatus == 2), merge_entries=False)
	
	def post_journal_entry(self):
		credit_account = frappe.db.get_value("Advance Type", self.advance_type, "advance_account")
	 
		
		voucher_type = "Journal Entry"
		voucher_series = "Journal Voucher"
		party_type = ""
		party = ""

		credit_account_type = frappe.db.get_value("Account", credit_account, "account_type")

	   


		if credit_account_type in ("Payable", "Receivable"):
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



		for item in self.expense_details:
			account=item.account
			broad_head = item.broad_head
			budget_activity = item.budget_activity
			budget_sub_activity = item.budget_sub_activity
			source_of_fund = item.source_of_fund
			
		if self.net_amount > 0:
			je.append("accounts", {
					"account": account,
					"reference_type": "Advance Settlement",
					"reference_name": self.name,
					"cost_center": self.cost_center,
					"debit_in_account_currency": flt(expense_amount),
					"debit": flt(expense_amount),
					"broad_head": broad_head,
					"budget_activity": budget_activity,
					"budget_sub_activity": budget_sub_activity,
					"source_of_fund": source_of_fund,

					})

			
			je.append("accounts", {
				"account": credit_account,
				"reference_type": "Advance Settlement",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(allocated_amount),
				"credit": flt(allocated_amount),
				"party_type": party_type,
				"party": party,
				"budget_activity": budget_activity,
				"budget_sub_activity": budget_sub_activity,
				"source_of_fund": source_of_fund

			})	
			je.append("accounts", {
				"account": credit_account,
				"reference_type": "Advance Settlement",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.net_amount),
				"credit": flt(self.net_amount),
				"party_type": party_type,
				"party": party,
				"budget_activity": budget_activity,
				"budget_sub_activity": budget_sub_activity,
				"source_of_fund": source_of_fund

			})
			if self.tds_amount > 0 :
				je.append("accounts", {
				"account": self.tds_account,
				"reference_type": "Advance Settlement",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.tds_amount),
				"credit": flt(self.tds_amount),
				"party_type": party_type,
				"party": party,
			})
			if self.retention_amount > 0:
				je.append("accounts", {
				"account": self.retention_account,
				"reference_type": "Advance Settlement",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.retention_amount),
				"credit": flt(self.retention_amount),
				"party_type": party_type,
				"party": party,
			})


			je.update({
				"doctype": "Journal Entry",
				"voucher_type": voucher_type,
				"naming_series": voucher_series,
				"title": self.name,
				"posting_date": self.posting_date,
				"company": self.company,
				"total_amount_in_words": money_in_words(self.net_amount),
				"branch": self.branch

			})

			

					
			
		
			
		je.insert()
		# frappe.db.commit()		
		self.db_set("journal_entry", je.name)
		frappe.msgprint("Journal Entry created. {}".format(frappe.get_desk_link("Journal Entry", je.name)))


	