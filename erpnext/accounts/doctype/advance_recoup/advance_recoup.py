# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt,nowtime,nowdate
from frappe.utils import money_in_words
from erpnext.custom_utils import prepare_gl
from frappe import _
from erpnext.custom_utils import check_budget_available

class AdvanceRecoup(Document):
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
		branch: DF.Link
		company: DF.Link | None
		cost_center: DF.Link | None
		customer: DF.DynamicLink | None
		expense_details: DF.Table[AdvanceRecoupItem]
		is_running_bill: DF.Check
		journal_entry: DF.Data | None
		party_type: DF.Literal["", "Customer", "Supplier", "Employee"]
		posting_date: DF.Date | None
		total_amount: DF.Currency
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
		if self.docstatus==0:
			self.calculate_amount()
		# self.check_budget_availability()
	
		
	def on_submit(self):
		if self.is_running_bill:
			self.update_general_ledger()
			self.post_journal_entry()
			self.make_mobilisation_entry()
	# def check_budget_availability(self):
	# 	for d in self.get("expense_details"):
	# 		if flt(d.amount) > 0:
	# 			# Determine the amount to check (debit or credit)
	# 			amount = flt(d.amount) 
				
	# 			account_type = frappe.db.get_value("Account", d.account, "account_type")
	# 			if account_type in ["Expense Account", "Income Account", "Expense", "Income"]:
	# 				check_budget_available(
	# 					cost_center=self.cost_center,
	# 					budget_account=d.account,
	# 					transaction_date=self.posting_date,
	# 					amount=amount,
						
	# 					budget_activity=d.budget_activity,
	# 					budget_sub_activity=d.budget_sub_activity,
	# 					source_of_fund=d.source_of_fund
	# 				)			


	# def calculate_amount(self):
	# 	total_balance=0
	# 	total_allocated=0
	# 	for d in self.advance_list:
	# 		if flt(d.allocated_amount) > flt(d.balance_amount):
	# 			frappe.throw(_("Allocated amount cannot be greater than balance amount"))
	# 		total_balance += flt(d.balance_amount)
	# 		total_allocated += flt(d.allocated_amount)
	# 		d.balance_amount = flt(total_balance) - flt(total_allocated)
	def calculate_amount(self):
		self.total_amount = 0
		for item in self.expense_details:
			self.total_amount += flt(item.amount)

		remaining = self.total_amount
		for d in self.advance_list:
			if remaining  >  d.balance_amount:
				d.allocated_amount = 0
				d.balance_amount = 0


		for d in self.advance_list:
			if flt(d.allocated_amount) >= flt(d.balance_amount):
				frappe.throw(_("Allocated amount cannot be greater than balance amount."))
			
				# d.balance_amount = 0
			d.allocated_amount = remaining
			d.balance_amount = flt(d.balance_amount) - remaining

		



			

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
			con.advance_recoup = self.name
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

		credit_account = frappe.db.get_value("Advance Type", self.advance_type, "advance_account")

		if not credit_account:
			frappe.throw("Please set Default Bank Account in Company")

		gl_entries.append(
			prepare_gl(self, {
				"account": credit_account,
				"credit": flt(self.opening_balance),
				"credit_in_account_currency": flt(self.opening_balance),
				"cost_center": self.cost_center,
		
			})
		)
	
		
		for d in self.expense_details:
			if d.amount > 0:
				je.append("accounts", {
					"account": d.account,
					"reference_type": "Advance Recoup",
					"reference_name": self.name,
					"cost_center": self.cost_center,
					"debit_in_account_currency": flt(d.amount),
					"debit": flt(d.amount),
					"broad_head": d.broad_head,
					"budget_activity": d.budget_activity,
					"budget_sub_activity": d.budget_sub_activity,
					"source_of_fund": d.source_of_fund,

				})
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
		amount = 0
		budget_activity:None
		budget_sub_activity:None
		source_of_fund:None
		for d in self.advance_list:
			amount += d.allocated_amount
		for item in self.expense_details:
			budget_activity = item.budget_activity
			budget_sub_activity = item.budget_sub_activity
			source_of_fund = item.source_of_fund
		if amount > 0:

			je.update({
				"doctype": "Journal Entry",
				"voucher_type": voucher_type,
				"naming_series": voucher_series,
				"title": "Advance Recoup - " + self.name,
				"posting_date": self.posting_date,
				"company": self.company,
				"total_amount_in_words": money_in_words(amount),
				"branch": self.branch

			})

			for d in self.expense_details:
				if d.amount > 0:
					je.append("accounts", {
						"account": d.account,
						"reference_type": "Advance Recoup",
						"reference_name": self.name,
						"cost_center": self.cost_center,
						"debit_in_account_currency": flt(d.amount),
						"debit": flt(d.amount),
						"broad_head": d.broad_head,
						"budget_activity": d.budget_activity,
						"budget_sub_activity": d.budget_sub_activity,
						"source_of_fund": d.source_of_fund,

					})
			je.append("accounts", {
				"account": credit_account,
				"reference_type": "Advance Recoup",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.total_amount),
				"credit": flt(self.total_amount),
				"party_type": party_type,
				"party": party,
				"budget_activity": budget_activity,
				"budget_sub_activity": budget_sub_activity,
				"source_of_fund": source_of_fund

			})	
		
			
		je.insert()
		# frappe.db.commit()		
		self.db_set("journal_entry", je.name)
		frappe.msgprint("Journal Entry created. {}".format(frappe.get_desk_link("Journal Entry", je.name)))


	