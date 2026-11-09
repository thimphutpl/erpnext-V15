# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import money_in_words,flt
from erpnext.custom_utils import prepare_gl


class OtherDepositClaim(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.other_deposit_item.other_deposit_item import OtherDepositItem
		from frappe.types import DF

		account_deposit: DF.Link
		amended_from: DF.Link | None
		branch: DF.Link
		company: DF.Link
		cost_center: DF.Link
		journal_entry: DF.Link | None
		other_deposite_details: DF.Table[OtherDepositItem]
		party: DF.DynamicLink
		party_type: DF.Literal["", "Customer", "Employee", "Supplier"]
		payment_status: DF.Data | None
		posting_date: DF.Date
		remarks: DF.SmallText | None
		total_amount: DF.Currency
	# end: auto-generated types

	def validate(self):
		self.calculate_total_amount()
		self.validate_claim_amount()
	

	def calculate_total_amount(self):
		self.total_amount = sum([d.amount_claim for d in self.other_deposite_details])
	def on_submit(self):
		self.post_journal_entry()
		self.calculate_balance()
		self.update_mof_entries()
	
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
					"Cannot cancel Other Deposit Claim {0} because linked Journal Entry {1}. "
					"Please Reject it first."
				).format(self.name, self.journal_entry)
		)
	def on_cancel(self):
		self.removed_journal_entry()
		self.cancel_mof_entries()

	def validate_claim_amount(self):
		for item in self.other_deposite_details:
			if not item.reference:
				continue

			balance = flt(
				frappe.db.get_value(
					"MOF Entry",
					item.reference,
					"balance_amount"
				)
			)

			item.balance_amount = balance

			if flt(item.amount_claim) > balance:
				frappe.throw(
					_("Amount Claim cannot be greater than Balance Amount for {0}. "
					"Amount Claim: {1}, Balance Amount: {2}").format(
						item.reference,
						item.amount_claim,
						balance
					)
				)


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
		je.title = "Other Deposit Claim - " + self.name
		je.remark = (
			remarkss
			if remarkss
			else "Note: Other Deposit Claim - " + self.name
		)
		je.posting_date = self.posting_date
		je.company = self.company
		je.total_amount_in_words = money_in_words(self.total_amount)
		je.branch = self.branch
		je.reference_doctype = self.doctype
		je.reference_link = self.name

		for item in self.other_deposite_details:
			je.append("accounts", {
				"account": self.account_deposit,
				"reference_type": "Other Deposit Claim",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"debit_in_account_currency": flt(self.total_amount),
				"debit": flt(self.total_amount),
				"party": item.party,
				"party_type":item.party_type,
				"ignore_budget_details":1

			})
		je.append("accounts", {
			"account": credit_account,
			"reference_type": "Other Deposit Claim",
			"reference_name": self.name,
			"cost_center": self.cost_center,
			"credit_in_account_currency": self.total_amount,
			"credit": self.total_amount,
			"ignore_budget_details":1
		})

		je.insert()
		self.db_set("journal_entry", je.name)
		frappe.msgprint("Journal Entry created. {}".format(frappe.get_desk_link("Journal Entry", je.name)))

	def removed_journal_entry(self):
				
		if not self.journal_entry:
			return

		je_name = self.journal_entry

		# Find linked Advance
		advance_name = frappe.db.get_value(
			"Other Deposit Claim",
			{"journal_entry": je_name},
			"name"
		)

		if advance_name:
			# Remove the Journal Entry link from Advance
			frappe.db.set_value(
				"Other Deposit Claim",
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
	def calculate_balance(self, cancel=False):
		for item in self.other_deposite_details:

	
			amount_claim = flt(item.amount_claim)
			# total_amount = flt(item.total_amount)
			balance_amount = flt(item.balance_amount)
			item.balance_amount = balance_amount - amount_claim
			if cancel:
				item.balance_amount = balance_amount + amount_claim
			else:
				item.balance_amount = balance_amount - amount_claim

			


			# if (balance_amount + allocated_amount) >= flt(item.advance_amount):
			# 	frappe.throw(
			# 	_("Allocated Amount cannot be greater than Advance Amount for {0}. "
			# 	"Allocated Amount: {1}, Balance Amount: {2}").format(
			# 		item.reference,
			# 		allocated_amount,
			# 		balance_amount
			
			# 	)
			# )




	def update_mof_entries(self, cancel=False):
		for row in self.other_deposite_details:

			if not row.reference:
				continue

			con = frappe.get_doc("MOF Entry", row.reference)

			claim_amount = flt(row.amount_claim)

			if cancel:
				con.claim_amount = flt(con.claim_amount) - claim_amount
			else:
				con.claim_amount = flt(con.claim_amount) + claim_amount
			con.balance_amount = (
				flt(con.amount) - flt(con.claim_amount)
			)
			con.flags.ignore_validate_update_after_submit = True
			con.save(ignore_permissions=True)
		
	def cancel_mof_entries(self):
		for row in self.other_deposite_details:
			if not row.reference:
				continue

			mof_entry = frappe.get_doc("MOF Entry", row.reference)

			amount = row.amount_claim or 0

			# Reverse claimed amount
			mof_entry.claim_amount = max(
				0,
				(mof_entry.claim_amount or 0) - amount
			)

			# Restore balance amount
			mof_entry.balance_amount = (
				(mof_entry.balance_amount or 0) + amount
			)

	
		

			mof_entry.save(ignore_permissions=True)
	def create_other_deposit_entries(self):
		for row in self.other_deposite_details:
			other_deposit_entry = frappe.new_doc("Other Deposit Entry")
			other_deposit_entry.company = self.company
			other_deposit_entry.posting_date = self.posting_date
			other_deposit_entry.branch = self.branch
			other_deposit_entry.cost_center = self.cost_center
			other_deposit_entry.account = row.account
			other_deposit_entry.party_type = row.party_type
			other_deposit_entry.party = row.party
			other_deposit_entry.amount = row.amount
			other_deposit_entry.amount_claim = row.amount_claim

			other_deposit_entry.other_deposit_claim = self.name
			other_deposit_entry.voucher_type = row.voucher_type
			other_deposit_entry.voucher_no = row.voucher_no
			other_deposit_entry.insert(ignore_permissions=True)

def _get_existing_cond():
	return """
		AND NOT EXISTS (
			SELECT 1
			FROM `tabOther Deposit Entry` ode
			WHERE ode.voucher_type = gl.voucher_type
				AND ode.voucher_no = gl.voucher_no
				AND ode.docstatus != 2
		)
	"""


@frappe.whitelist()
def get_all_other_deposit(company, account_deposit, party_type, party):
	data = frappe.db.sql(f"""
		SELECT
			me.name,
			me.amount,
			me.account,
			me.balance_amount,
			me.party,
			me.party_type,
			me.board_head,
			me.is_opening
		FROM `tabMOF Entry` me
		WHERE
			me.account = %s
			AND me.company = %s
			AND me.party_type = %s
			AND me.party = %s
			AND me.is_cancelled = 0
			AND me.balance_amount > 0
			
	""", (
		account_deposit,
		company,
		party_type,
		party,
	
	), as_dict=True)

	return data
# @frappe.whitelist()
# def get_all_other_deposit(company, account_deposit, party_type, party, posting_date):

# 	existing_cond = _get_existing_cond()

# 	data = frappe.db.sql(f"""
# 		SELECT
# 			gl.name,
# 			gl.credit AS amount,
# 			gl.account,
# 			gl.party,
# 			gl.party_type,
# 			gl.voucher_type,
# 			gl.voucher_no,
# 			gl.is_opening,
# 			gl.remarks as assignment
# 		FROM `tabGL Entry` gl
# 		WHERE
# 			gl.account = %s
# 			AND gl.company = %s
# 			AND gl.party_type = %s
# 			AND gl.party = %s
# 			AND gl.is_cancelled = 0
# 			AND gl.credit > 0
# 			AND gl.posting_date <= %s
# 			AND gl.is_opening IN ('Yes')
# 			{existing_cond}
# 	""", (
# 		account_deposit,
# 		company,
# 		party_type,
# 		party,
# 		posting_date
# 	), as_dict=True)

# 	return data
# @frappe.whitelist()
# def get_other_deposit_claim(voucher_type, voucher_no):
#     claim = frappe.db.get_value(
#         "Other Deposit Entry",
#         {
#             "voucher_type": voucher_type,
#             "voucher_no": voucher_no,
#             "docstatus": ["!=", 2]
#         },
#         "other_deposit_claim"
#     )

#     return claim