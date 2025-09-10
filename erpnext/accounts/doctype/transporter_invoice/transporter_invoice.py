# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from erpnext.custom_utils import check_future_date
from erpnext.controllers.accounts_controller import AccountsController
from frappe.utils import flt, cint, money_in_words
from erpnext.accounts.general_ledger import (
	get_round_off_account_and_cost_center,
	make_gl_entries,
	make_reverse_gl_entries,
	merge_similar_entries,
)


class TransporterInvoice(AccountsController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.transporter_invoice_item.transporter_invoice_item import TransporterInvoiceItem
		from frappe.types import DF

		amended_from: DF.Link | None
		amount: DF.Currency
		branch: DF.Link
		company: DF.Link
		cost_center: DF.Link
		credit_account: DF.Link | None
		currency: DF.Link | None
		equipment: DF.Data | None
		expense_account: DF.Link | None
		journal_entry: DF.Data | None
		landed_cost_voucher: DF.Link | None
		posting_date: DF.Date
		status: DF.Literal["", "Paid", "Unpaid", "Submitted", "Partly Paid", "Draft", "Cancelled"]
		supplier: DF.Link
		title: DF.Data | None
		transportation_details: DF.Table[TransporterInvoiceItem]
	# end: auto-generated types
	pass

	def validate(self):
		check_future_date(self.posting_date)
		#validate duplicate
		for d in frappe.get_all("Transporter Invoice", {"landed_cost_voucher": self.landed_cost_voucher, "name": ("!=", self.name), "docstatus": ("<", 2)}, "name"):
			frappe.throw(f"There exist another {frappe.get_desk_link('Transporter Invoice', d.name)} against this Landed Cost")

		self.get_items_data()
		self.set_status()

	def before_submit(self):
		if not self.expense_account or not self.credit_account:
			frappe.throw("Expense/Credit Account missing.")

	def set_status(self, update=False, status=None, update_modified=True):
		if self.is_new():
			self.status = "Draft"
			return

		# outstanding_amount = flt(self.outstanding_amount,2)
		if not status:
			if self.docstatus == 2:
				status = "Cancelled"
			elif self.docstatus == 1:
				self.status = "Paid"
			else:
				self.status = "Unpaid"

		if update:
			self.db_set("status", self.status, update_modified=update_modified)

	def on_submit(self):
		self.make_gl_entries()

	def on_cancel(self):
		self.ignore_linked_doctypes = ("GL Entry", "Stock Ledger Entry", "Payment Ledger Entry")
		self.make_gl_entries()

	def get_items_data(self):
		if not self.amount:
			self.amount = frappe.get_value("Landed Cost Voucher", self.landed_cost_voucher, "total_taxes_and_charges")

		self.set("transportation_details",[])
		for item in frappe.get_all("Landed Cost Purchase Receipt", {"parent": self.landed_cost_voucher, "parenttype": "Landed Cost Voucher"}, ["name", "posting_date", "receipt_document", "grand_total"]):
			row = self.append("transportation_details",{})
			row.update({"posting_date": item.posting_date,
            		"reference_name": item.receipt_document,
            		"amount": item.grand_total})

	def make_gl_entries(self):
		gl_entries = []
		self.make_supplier_gl_entry(gl_entries)
		self.make_expense_gl_entries(gl_entries)
		gl_entries = merge_similar_entries(gl_entries)
		make_gl_entries(gl_entries,update_outstanding="No",cancel=self.docstatus == 2)

	def make_supplier_gl_entry(self, gl_entries):
		if flt(self.amount) > 0:
			# Did not use base_grand_total to book rounding loss gle
			gl_entries.append(
				self.get_gl_dict({
					"account": self.credit_account,
					"credit": flt(self.amount,2),
					"credit_in_account_currency": flt(self.amount,2),
					"against_voucher": self.name,
					"party_type": "Supplier",
					"party": self.supplier,
					"against_voucher_type": self.doctype,
					"cost_center": self.cost_center,
					"voucher_type":self.doctype,
					"voucher_no":self.name
				}, self.currency))

	def make_expense_gl_entries(self, gl_entries):
		gl_entries.append(
			self.get_gl_dict({
					"account":  self.expense_account,
					"debit": flt(self.amount,2),
					"debit_in_account_currency": flt(self.amount,2),
					"against_voucher": self.name,
					"against_voucher_type": self.doctype,
					"cost_center": self.cost_center,
					"voucher_type":self.doctype,
					"voucher_no":self.name
			}, self.currency)
		)

	@frappe.whitelist()
	def post_journal_entry(self):
		if self.journal_entry and frappe.db.exists("Journal Entry",{"name":self.journal_entry,"docstatus":("!=",2)}):
			frappe.msgprint(_("Journal Entry Already Exists {}".format(frappe.get_desk_link("Journal Entry",self.journal_entry))))
		if not self.amount:
			frappe.throw(_("Payable Amount should be greater than zero"))
			
		# default_ba = get_default_ba()

		credit_account = self.credit_account
	
		if not credit_account:
			frappe.throw("Expense Account is mandatory")
		r = []
		r.append(_("Note: {0}").format(self.name))

		remarks = ("").join(r) #User Remarks is not mandatory
		bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		if not bank_account:
			frappe.throw(_("Default bank account is not set in Branch {}".format(frappe.bold(self.branch))))
		# Posting Journal Entry
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions=1
		je.update({
			"doctype": "Journal Entry",
			"voucher_type": "Bank Entry",
			"naming_series": "Bank Payment Voucher",
			"title": "Transporter Payment "+ self.supplier,
			"user_remark": "Note: " + "Transporter Payment - " + self.supplier,
			"posting_date": self.posting_date,
			"company": self.company,
			"total_amount_in_words": money_in_words(self.amount),
			"branch": self.branch,
			"reference_type":self.doctype,
			"referece_doctype":self.name
		})
		je.append("accounts",{
			"account": credit_account,
			"debit_in_account_currency": self.amount,
			"cost_center": self.cost_center,
			"party_check": 1,
			"party_type": "Supplier",
			"party": self.supplier,
			"reference_type": self.doctype,
			"reference_name": self.name
		})
		je.append("accounts",{
			"account": bank_account,
			"credit_in_account_currency": self.amount,
			"cost_center": self.cost_center
		})

		je.insert()
		#Set a reference to the claim journal entry
		self.db_set("journal_entry",je.name)
		frappe.msgprint(_('{0} posted to accounts').format(frappe.get_desk_link("Journal Entry",je.name)))
	