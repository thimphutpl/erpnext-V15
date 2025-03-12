# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from frappe.utils import cint, cstr, flt, formatdate, get_link_to_form, getdate, nowdate, now_datetime


class POLAdvance(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		adjusted_amount: DF.Currency
		advance_amount: DF.Currency
		amended_from: DF.Link | None
		balance_amount: DF.Currency
		branch: DF.Link
		company: DF.Link | None
		cost_center: DF.Link | None
		equipment: DF.Link
		equipment_name: DF.Data | None
		fuelbook: DF.Link
		is_opening: DF.Check
		journal_entry: DF.Data | None
		journal_entry_status: DF.Data | None
		posting_date: DF.Date
		status: DF.Literal["Draft", "Paid", "Unpaid", "Cancelled"]
		supplier: DF.Link
	# end: auto-generated types
	
	def validate(self):
		self.set_status()

	def on_submit(self):
		if not self.is_opening:
			self.post_journal_entry()
		else:
			self.status = "Paid"

	def on_cancel(self):
		self.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry")

	def set_status(self, status=None):
		if self.is_new():
			if self.get("amended_from"):
				self.status = "Draft"
			return

		if not status:
			if self.docstatus == 2:
				status = "Cancelled"
			elif self.docstatus == 1:
				self.status = "Unpaid"
		else:
			self.status = "Draft"

	def post_journal_entry(self):
		default_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		advance_account = frappe.db.get_value("Company", self.company, "pol_advance_account")

		if not default_bank_account:
			frappe.throw(
				"Default Expense Bank Account is not set for {}. Please configure it in the Branch.".format(
					frappe.get_desk_link("Branch", self.branch)
				),
				title="Missing Account"
			)

		if not advance_account:
			frappe.throw(
				"POL Advance Account is not set for {}. Please configure it in the Company.".format(
					frappe.get_desk_link("Company", self.company)
				),
				title="Missing Account"
			)

		# Posting Journal Entry
		accounts = []
		accounts.append({
			"account": advance_account,
			"debit": flt(self.advance_amount),
			"debit_in_account_currency": flt(self.advance_amount),
			"cost_center": self.cost_center,
			"party_check": 1,
			"party_type": "Supplier",
			"party": self.supplier,
			"is_advance": "Yes",
			"reference_type": self.doctype,
			"reference_name": self.name,
		})

		accounts.append({
			"account": default_bank_account,
			"credit": flt(self.advance_amount),
			"credit_in_account_currency": flt(self.advance_amount),
			"cost_center": self.cost_center,
		})

		je = frappe.new_doc("Journal Entry")
		voucher_type = "Bank Entry"
		naming_series = "Bank Payment Voucher"
		
		je.update({
				"doctype": "Journal Entry",
				"voucher_type": voucher_type,
				"naming_series": naming_series,
				"title": "POL Advance - "+self.equipment,
				"user_remark": "POL Advance - "+self.equipment,
				"posting_date": nowdate(),
				"company": self.company,
				"accounts": accounts,
				"branch": self.branch
		})

		je.save(ignore_permissions = True)
		self.db_set("journal_entry", je.name)
		self.db_set("journal_entry_status", "Forwarded to accounts for processing payment on {0}".format(now_datetime().strftime('%Y-%m-%d %H:%M:%S')))
		frappe.msgprint(_('{} posted to accounts').format(frappe.get_desk_link(je.doctype,je.name)))

