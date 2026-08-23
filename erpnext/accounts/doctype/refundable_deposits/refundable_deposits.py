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
		account_deposit: DF.Link
		amended_from: DF.Link | None
		amount: DF.Currency
		board_head: DF.Link
		branch: DF.Link
		company: DF.Link
		cost_center: DF.Link
		journal_entry: DF.Link | None
		other_deposits: DF.Table[MOFPaymentItem]
		party: DF.DynamicLink
		party_type: DF.Literal["", "Employee", "Customer", "Employee"]
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
	
	
	def post_journal_entry(self):
		credit_account = frappe.db.get_value(
			"Company",
			self.company,
			"default_bank_account"
		)

		if not credit_account:
			frappe.throw("Setup Default Bank Account in Company Settings")

		

		voucher_type = "Disbursement Voucher"
		voucher_series = "Disbursement Voucher"

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
		je.total_amount_in_words = money_in_words(self.amount)
		je.branch = self.branch
		je.reference_doctype = self.doctype
		je.reference_link = self.name

	
		je.append("accounts", {
			"account": self.account,
			"reference_type": "Refundable Deposits",
			"reference_name": self.name,
			"cost_center": self.cost_center,
			"debit_in_account_currency": flt(self.amount),
			"debit": flt(self.amount),
			"party_type" : self.party_type,
			"party" :self.party,
			"ignore_budget_details":1
			
		})
		je.append("accounts", {
			"account": credit_account,
			"reference_type": "Refundable Deposits",
			"reference_name": self.name,
			"cost_center": self.cost_center,
			"credit_in_account_currency": self.amount,
			"credit": self.amount,
			"ignore_budget_details":1
		})

		je.insert()
		self.db_set("journal_entry", je.name)
		frappe.msgprint("Journal Entry created. {}".format(frappe.get_desk_link("Journal Entry", je.name)))


	def create_mof_entries(self):
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
			mof_entry.amount = row.amount
			mof_entry.refundable_deposits = self.name
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
			{existing_cond}
	""", (
		account_deposit,
		company,
		posting_date
	), as_dict=True)

	return data
