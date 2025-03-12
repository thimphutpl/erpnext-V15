# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from frappe.utils import (
	add_days,
	ceil,
	cint,
	cstr,
	date_diff,
	floor,
	flt,
	formatdate,
	get_first_day,
	get_last_day,
	get_link_to_form,
	getdate,
	money_in_words,
	rounded,
	nowdate
)

class VisitorPassRegistry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.event_management.doctype.visitor_pass_registry_item.visitor_pass_registry_item import VisitorPassRegistryItem
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		cashier: DF.Link
		company: DF.Link | None
		cost_center: DF.Link | None
		items: DF.Table[VisitorPassRegistryItem]
		journal_entry: DF.Data | None
		location: DF.Link
		posting_date: DF.Date
		status: DF.Literal["", "Draft", "Submitted", "Closed", "Cancelled"]
		total_amount: DF.Currency
		total_csr_amount: DF.Currency
		total_visitors: DF.Int
	# end: auto-generated types
	
	def validate(self):
		self.validate_amount()

	def on_submit(self):
		self.post_journal_entry()

	def on_cancel(self):
		self.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry")

	def validate_amount(self):
		total_amount, total_csr_amount, total_visitor = 0.0, 0.0, 0
		for d in self.items:
			d.amount = flt(d.qty) * flt(d.ticket_price)
			total_amount += flt(d.amount)
			total_csr_amount += flt(d.csr_amount)
			total_visitor += flt(d.no_of_visitors)
		self.total_visitors = flt(total_visitor)
		self.total_amount = flt(total_amount)
		self.total_csr_amount = flt(total_csr_amount)

	def post_journal_entry(self):
		income_account = frappe.db.get_value("Location", self.location, "income_account")
		csr_account = frappe.db.get_value("Company", self.company, "csr_account")

		if not csr_account:
			frappe.throw(
				"CSR Account is not set for {}. Please configure it in the company.".format(
					frappe.get_desk_link("Company", self.company)
				),
				title="Missing Account"
			)

		if not income_account:
			frappe.throw(
				"Income Account is not set for {}. Please configure it in the Location.".format(
					frappe.get_desk_link("Location", self.location)
				),
				title="Missing Account"
			)

		# Posting Journal Entry
		accounts = []
		for d in self.get("items"):
			account = get_bank_cash_account(d.mode_of_payment, self.company)
			accounts.append({
				"account": account,
				"debit_in_account_currency": flt(d.amount),
				"cost_center": self.cost_center,
				"reference_type": self.doctype,
				"reference_name": self.name,
			})

			if flt(d.no_of_visitors) - flt(d.qty) > 0:
				accounts.append({
					"account": csr_account,
					"debit_in_account_currency": flt(d.csr_amount),
					"cost_center": self.cost_center,
					"reference_type": self.doctype,
					"reference_name": self.name,
				})

		accounts.append({
			"account": income_account,
			"credit_in_account_currency": flt(self.total_amount)+flt(self.total_csr_amount),
			"cost_center": self.cost_center,
		})

		je = frappe.new_doc("Journal Entry")
		
		voucher_type = "Journal Entry"
		naming_series = "Journal Voucher"
		
		je.update({
				"doctype": "Journal Entry",
				"voucher_type": voucher_type,
				"naming_series": naming_series,
				"title": "Visitor Pass Registry - "+self.location,
				"user_remark": "Visitor Pass Registry - "+self.location,
				"posting_date": self.posting_date,
				"company": self.company,
				"accounts": accounts,
				"branch": self.branch
		})

		je.save(ignore_permissions = True)
		je.submit()
		self.db_set("journal_entry", je.name)
		# self.db_set("journal_entry_status", "Forwarded to accounts for processing payment on {0}".format(now_datetime().strftime('%Y-%m-%d %H:%M:%S')))
		frappe.msgprint(_('{} posted to accounts').format(frappe.get_desk_link(je.doctype,je.name)))

@frappe.whitelist()
def get_bank_cash_account(mode_of_payment, company):
	account = frappe.db.get_value(
		"Mode of Payment Account", {"parent": mode_of_payment, "company": company}, "default_account"
	)
	if not account:
		frappe.throw(
			_("Please set default Cash or Bank account in Mode of Payment {0}").format(
				get_link_to_form("Mode of Payment", mode_of_payment)
			),
			title=_("Missing Account"),
		)
	return account