# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, formatdate, getdate, money_in_words, nowdate

# from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states

class ImprestAdvance(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		adjusted_amount: DF.Currency
		advance_amount: DF.Currency
		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Link | None
		approver_name: DF.Data | None
		balance_amount: DF.Currency
		branch: DF.Link
		company: DF.Link | None
		cost_center: DF.Link
		is_opening: DF.Check
		journal_entry: DF.Data | None
		opening_amount: DF.Currency
		party: DF.DynamicLink
		party_type: DF.Literal["", "Employee", "Agency"]
		posting_date: DF.Date
		remarks: DF.SmallText | None
	# end: auto-generated types

	def validate(self):
		self.validate_advance_amount()

	def before_cancel(self):
		if self.journal_entry:
			ab_status = frappe.get_value("Journal Entry", {"name": self.journal_entry}, "docstatus")
			if cint(ab_status) == 1:
				frappe.throw("Journal Entry {} for this transaction needs to be cancelled first".format(frappe.get_desk_link("Journal Entry", self.journal_entry)))
			else:
				frappe.db.sql(f"delete from `tabJournal Entry` where name = '{self.journal_entry}'")
				self.db_set("journal_entry", None)

	def validate_advance_amount(self):
		if not self.is_opening:
			pass

	def on_submit(self):
		if not self.is_opening:
			self.post_journal_entry()

	def on_cancel(self):
		# if self.imprest_recoup:
		# 	frappe.throw("Imprest Recoup <b>{}</b> needs to to cancelled first.".format(self.imprest_recoup))
		pass

	def post_journal_entry(self):
		imprest_advance_account = frappe.db.get_value("Company", self.company, "imprest_advance_account")
		bank_account = frappe.db.get_value("Company", self.company, "default_bank_account")
		if not bank_account:
			frappe.throw(f"Set default bank account in company {frappe.bold(self.company)}")
		if not imprest_advance_account:
			frappe.throw("Set Imprest Advance Account in {}".format(
				frappe.get_desk_link("Company", self.company)
			))
		accounts = []
		accounts.append({
			"account": imprest_advance_account,
			"cost_center": self.cost_center,
			"party_type": self.party_type,
			"party": self.party,
			"debit": self.advance_amount,
			"debit_in_account_currency": self.advance_amount,
			"reference_type": self.doctype,
			"reference_name": self.name
		})
		accounts.append({
			"account": bank_account,
			"cost_center": self.cost_center,
			"credit": self.advance_amount,
			"credit_in_account_currency": self.advance_amount,
			"reference_type": self.doctype,
			"reference_name": self.name
		})

		ab = frappe.new_doc("Journal Entry")
		ab.flags.ignore_permission = 1
		ab.update({
			"doctype": "Journal Entry",
			"voucher_type": "Bank Entry",
			"naming_series": "Bank Payment Voucher",
			"posting_date": self.posting_date,
			"company": self.company,
			"branch": self.branch,
			# "reference_doctype": self.doctype,
			# "reference_name": self.name,
			"accounts": accounts,
		})
		ab.insert()
		self.db_set('journal_entry', ab.name)
		frappe.msgprint(_('Journal Entry {0} posted').format(frappe.get_desk_link("Journal Entry", ab.name)))
