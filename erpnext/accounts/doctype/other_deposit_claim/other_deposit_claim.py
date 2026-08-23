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
	

	def calculate_total_amount(self):
		self.total_amount = sum([d.amount for d in self.other_deposite_details])
	def on_submit(self):
		self.post_journal_entry()
		self.create_other_deposit_entries()

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
def get_all_other_deposit(company, account_deposit, party_type, party, posting_date):

	existing_cond = _get_existing_cond()

	data = frappe.db.sql(f"""
		SELECT
			gl.name,
			gl.credit AS amount,
			gl.account,
			gl.party,
			gl.party_type,
			gl.voucher_type,
			gl.voucher_no
		FROM `tabGL Entry` gl
		WHERE
			gl.account = %s
			AND gl.company = %s
			AND gl.party_type = %s
			AND gl.party = %s
			AND gl.is_cancelled = 0
			AND gl.credit > 0
			AND gl.posting_date <= %s
			{existing_cond}
	""", (
		account_deposit,
		company,
		party_type,
		party,
		posting_date
	), as_dict=True)

	return data
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