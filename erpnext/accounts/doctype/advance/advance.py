# # Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import money_in_words
from erpnext.custom_utils import prepare_gl
from frappe.utils import flt
class Advance(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link | None
		advance_amount: DF.Float
		advance_type: DF.Link
		amended_from: DF.Link | None
		branch: DF.Link | None
		budget_activity: DF.Link
		budget_sub_activity: DF.Link
		company: DF.Link
		cost_center: DF.Link | None
		customer: DF.DynamicLink
		customer_cid: DF.Data | None
		employee: DF.Link | None
		employee_name: DF.Data | None
		is_opening: DF.Check
		item_code: DF.Data | None
		item_name: DF.Data | None
		opening_balance: DF.Float
		party_type: DF.Literal["", "Customer", "Supplier", "Employee"]
		posting_date: DF.Date | None
		remarks: DF.SmallText | None
		source_of_fund: DF.Link
	# end: auto-generated types

	def validate(self):
		"""Validate document before save"""
		self.validate_required_fields()
		self.validate_advance_amount()

	def validate_required_fields(self):
		"""Check if all required fields are present"""
		required_fields = ["company", "customer", "advance_amount", "posting_date"]
		for field in required_fields:
			if not self.get(field):
				frappe.throw(_("{0} is required").format(self.meta.get_field(field).label))

	def validate_advance_amount(self):
		"""Validate advance amount is positive"""
		if self.advance_amount <= 0:
			frappe.throw(_("Advance Amount must be greater than zero"))

	def on_submit(self):
		self.update_general_ledger()
		self.post_journal_entry()


	def update_general_ledger(self):
		gl_entries = []
		debit_account = frappe.db.get_value("Company", self.company, "default_payable_account")
		credit_account = frappe.db.get_value("Company", self.company, "default_receivable_account")
		gl_entries.append(
			prepare_gl(self, {
				"account":debit_account,
				"credit": flt(self.advance_amount),
				"credit_in_account_currency": flt(self.advance_amount),
				"cost_center": self.cost_center,
			
			})
		)
		gl_entries.append(
			prepare_gl(self, {
				"account": credit_account,
				"debit": flt(self.advance_amount),
				"debit_in_account_currency": flt(self.advance_amount),
				"cost_center": self.cost_center,
			
			})
		)
		if gl_entries:
			from erpnext.accounts.general_ledger import make_gl_entries
			make_gl_entries(gl_entries, cancel=(self.docstatus == 2), merge_entries=False)	

	def post_journal_entry(self):
		debit_account = frappe.db.get_value("Company", self.company, "default_payable_account")
		credit_account = frappe.db.get_value("Company", self.company, "default_receivable_account")
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = f"Advance - {self.name}",
		je.voucher_type = 'Journal Entry'
		je.naming_series = 'Journal Voucher'
		je.remark = 'Payment against : ' + self.name
		je.posting_date = self.posting_date
		je.company = self.company
		je.branch = self.branch
		je.customer = self.customer
		je.advance_type = self.advance_type
		je.account = self.account
		if self.advance_amount > 0:
			je.append("accounts", {
				"account": credit_account,
				"reference_type": "Advance",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.advance_amount),
				"credit": flt(self.advance_amount),
				"party_type": self.party_type,
				"party": self.customer,
			})
			je.append("accounts", {
				"account": debit_account,
				"reference_type": "Advance",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"debit_in_account_currency": flt(self.advance_amount),
				"debit": flt(self.advance_amount),
				"party_type": self.party_type,
				"party": self.customer,
			})
			
		je.save()
		frappe.db.commit()		



# @frappe.whitelist()
# def get_advance(customer, branch):
#     if not customer:
#         frappe.throw(_("Customer is required"))
#     filters = {
#         "customer": customer,
#         "docstatus": 1  # Only submitted documents
#     }
#     if branch:
#         filters["branch"] = branch
#     advances = frappe.db.get_all(
#         "Mobilisation Entry",
#         filters=filters,
#         fields=["name","account","advance_amount", "advance_type"]
#     )
	
#     return advances




