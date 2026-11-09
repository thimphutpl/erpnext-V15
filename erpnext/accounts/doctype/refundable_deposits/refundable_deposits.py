# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import money_in_words,flt
from erpnext.custom_utils import prepare_gl

class RefundableDeposits(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.mof_payment_item.mof_payment_item import MOFPaymentItem
		from frappe.types import DF

		account: DF.Link
		account_deposit: DF.Link | None
		amended_from: DF.Link | None
		amount: DF.Currency
		board_head: DF.Link
		branch: DF.Link
		company: DF.Link
		cost_center: DF.Link
		is_opening: DF.Check
		journal_entry: DF.Link | None
		opening_balance: DF.Currency
		other_deposits: DF.Table[MOFPaymentItem]
		party: DF.DynamicLink
		party_type: DF.Literal["", "Employee", "Customer", "Supplier"]
		posting_date: DF.Date
		remarks: DF.SmallText | None
	# end: auto-generated types

	
	def validate(self):
		
		self.calculate_total_amount()
	

	def calculate_total_amount(self):
		total_amount = 0
		for item in self.other_deposits:
			total_amount += item.amount
		self.amount = total_amount

	def on_submit(self):
		self.post_journal_entry()
		self.create_mof_entries()
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
					"Cannot cancel Refundable Deposits {0} because linked Journal Entry {1}. "
					"Please Reject it first."
				).format(self.name, self.journal_entry)
		)
	def on_cancel(self):
		self.removed_journal_entry()
		self.cancel_mof_entries()

	def cancel_mof_entries(self):

		frappe.db.set_value(
			"MOF Entry",
			{"mof_payment": self.name},
			"is_cancelled",
			1
		)
		
	def removed_journal_entry(self):
			
		if not self.journal_entry:
			return

		je_name = self.journal_entry

		# Find linked Advance
		advance_name = frappe.db.get_value(
			"Refundable Deposits",
			{"journal_entry": je_name},
			"name"
		)

		if advance_name:
			# Remove the Journal Entry link from Advance
			frappe.db.set_value(
				"Refundable Deposits",
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
	
	
	def post_journal_entry(self):
		credit_account = frappe.db.get_value(
			"Company",
			self.company,
			"default_temporary_account" if self.is_opening else "default_bank_account"
		)

		# if not credit_account:

		# 	frappe.throw("Setup Default Bank Account in Company Settings")
		if not credit_account:
			frappe.throw(
				_("Please configure {0} in Company Settings.").format(
					"Default Temporary Account" if self.is_opening else "Default Bank Account"
				)
	)
		

		# voucher_type = "Disbursement Voucher"
		# voucher_series = "Disbursement Voucher"
		voucher_type = "Opening Entry" if self.is_opening else "Disbursement Voucher"
		voucher_series = "Opening Entry" if self.is_opening else "Disbursement Voucher"

		naming_series = frappe.db.get_value(
			"Journal Entry Series",
			voucher_series,
			"name"
		)

		if not naming_series:
			frappe.throw(
				_("Journal Entry Series is not configured for {0}").format(
					voucher_series
				)
			)

		remarks = []

		if self.remarks:
			remarks.append(_("Note: {0}").format(self.remarks))

		remarkss = "".join(remarks)

		je = frappe.new_doc("Journal Entry")

		je.voucher_type = voucher_type
		je.naming_series = naming_series
		je.title = "Refundable Deposits - " + self.name
		je.remark = (
			remarkss
			if remarkss
			else "Note: Refundable Deposits- " + self.name
		)
		je.posting_date = self.posting_date
		je.company = self.company
		je.total_amount_in_words = money_in_words(self.opening_balance if self.is_opening else self.amount)
		je.branch = self.branch
		je.reference_doctype = self.doctype
		je.reference_link = self.name

		if self.is_opening:
			je.append("accounts", {
					"account": credit_account ,
					"reference_type": "Refundable Deposits",
					"reference_name": self.name,
					"cost_center": self.cost_center,
					"debit_in_account_currency": flt(self.opening_balance if self.is_opening else self.amount),
					"debit": flt(self.opening_balance if self.is_opening else self.amount),
					"ignore_budget_details":1
					
				})
			je.append("accounts", {
				"account": self.account,
				"reference_type": "Refundable Deposits",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": self.opening_balance if self.is_opening else self.amount,
				"credit": self.opening_balance if self.is_opening else self.amount,
				"party_type" : self.party_type,
				"party" :self.party,
				"ignore_budget_details":1
			})
		else:
			je.append("accounts", {
				"account": self.account,
				"reference_type": "Refundable Deposits",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"debit_in_account_currency": flt(self.opening_balance if self.is_opening else self.amount),
				"debit": flt(self.opening_balance if self.is_opening else self.amount),
				"party_type" : self.party_type,
				"party" :self.party,
				"ignore_budget_details":1
				
			})
			je.append("accounts", {
				"account": credit_account,
				"reference_type": "Refundable Deposits",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": self.opening_balance if self.is_opening else self.amount,
				"credit": self.opening_balance if self.is_opening else self.amount,
				"ignore_budget_details":1
			})

		je.insert()
		self.db_set("journal_entry", je.name)
		frappe.msgprint("Journal Entry created. {}".format(frappe.get_desk_link("Journal Entry", je.name)))


	def create_mof_entries(self):
		if self.is_opening:
			mof_entry = frappe.new_doc("MOF Entry")
			mof_entry.company = self.company
			mof_entry.posting_date = self.posting_date
			mof_entry.branch = self.branch
			mof_entry.cost_center = self.cost_center
			mof_entry.board_head = self.board_head
			mof_entry.account = self.account
			mof_entry.party_type = self.party_type
			mof_entry.party = self.party
			mof_entry.amount = self.opening_balance
			mof_entry.is_opening = self.is_opening
			mof_entry.balance_amount = self.opening_balance
			mof_entry.mof_payment = self.name
			mof_entry.voucher_type = "Journal Entry"
			mof_entry.voucher_no = self.journal_entry
			mof_entry.insert(ignore_permissions=True)
		else:

			for row in self.other_deposits:
				mof_entry = frappe.new_doc("MOF Entry")
				mof_entry.company = self.company
				mof_entry.posting_date = self.posting_date
				mof_entry.branch = self.branch
				mof_entry.cost_center = self.cost_center
				mof_entry.board_head = self.board_head
				mof_entry.account = row.account
				mof_entry.party_type = row.party_type
				mof_entry.party = row.party
				mof_entry.amount = self.amount
				mof_entry.balance_amount = self.amount
				mof_entry.mof_payment = self.name
				mof_entry.voucher_type = row.voucher_type
				mof_entry.voucher_no = row.voucher_no
				mof_entry.insert(ignore_permissions=True)
		
def _get_existing_cond():
	return """
		AND NOT EXISTS (
			SELECT 1
			FROM `tabMOF Entry` me
			WHERE me.voucher_type = gl.voucher_type
				AND me.voucher_no = gl.voucher_no
				AND me.docstatus != 2
		)
	"""


@frappe.whitelist()
def get_all_other_deposit(company, account_deposit, posting_date):

	existing_cond = _get_existing_cond()

	data = frappe.db.sql(f"""
		SELECT
			gl.name AS source_gl_entry,
			gl.credit AS outstanding,
			gl.account,
			gl.party,
			gl.party_type,
			gl.voucher_type,
			gl.voucher_no
		FROM `tabGL Entry` gl
		WHERE gl.account = %s
			AND gl.credit > 0
			AND gl.company = %s
			AND gl.is_cancelled = 0
			AND gl.posting_date <= %s
			AND gl.is_opening IN ('No')
			{existing_cond}
	""", (
		account_deposit,
		company,
		posting_date
	), as_dict=True)

	return data
