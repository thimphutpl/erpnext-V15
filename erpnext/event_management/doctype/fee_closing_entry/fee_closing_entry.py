# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from frappe import _
from frappe.utils import flt, getdate, get_link_to_form


class FeeClosingEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.event_management.doctype.entry_fee_reference.entry_fee_reference import EntryFeeReference
		from erpnext.event_management.doctype.payment_method_detail.payment_method_detail import PaymentMethodDetail
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		cashier: DF.Link | None
		company: DF.Link | None
		cost_center: DF.Link | None
		grand_total: DF.Currency
		journal_entry: DF.Data | None
		location: DF.Link | None
		payments: DF.Table[PaymentMethodDetail]
		posting_date: DF.Date
		references: DF.Table[EntryFeeReference]
		status: DF.Literal["Draft", "Open", "Submitted", "Cancelled"]
	# end: auto-generated types
	
	def validate(self):
		self.validate_duplicate_reference_docs()
		self.validate_reference_docs()

	def on_submit(self):
		self.post_journal_entry()
		self.update_reference_status()

	def on_cancel(self):
		self.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry")
		self.update_reference_status(cancel=True)

	def update_reference_status(self, cancel=False):
		status = 'Open' if cancel else 'Closed'
		for d in self.get("references"):
			try:
				doc = frappe.get_doc("Visitor Pass Registry", d.reference_name)
				doc.update_status(status)
				doc.save(ignore_permissions=True)
			except frappe.DoesNotExistError:
				frappe.msgprint(f"Reference {d.reference_name} not found!", alert=True)

	def validate_duplicate_reference_docs(self):
		ref_occurances = {}
		for idx, ref in enumerate(self.references, 1):
			ref_occurances.setdefault(ref.reference_name, []).append(idx)

		error_list = []
		for key, value in ref_occurances.items():
			if len(value) > 1:
				error_list.append(
					_("{0} is added multiple times on rows: {1}").format(frappe.bold(key), frappe.bold(value))
				)
			
		if error_list:
			frappe.throw(error_list, title=_("Duplicate Reference found"), as_list=True)

	def validate_reference_docs(self):
		invalid_rows = []
		for d in self.references:
			invalid_row = {"idx": d.idx}
			ref_doc = frappe.db.get_values(
				"Visitor Pass Registry",
				d.reference_name,
				["location", "cashier", "docstatus"],
				as_dict=1,
			)[0]

			if ref_doc.location != self.location:
				invalid_row.setdefault("msg", []).append(_("Location {} doesn't match with {}".format(
					frappe.bold(self.location),
					
					)))
				invalid_rows.append(invalid_row)
				continue
			if ref_doc.docstatus != 1:
				invalid_row.setdefault("msg", []).append(_("Visitor Pass Registry is not submitted"))
			if ref_doc.cashier != self.cashier:
				invalid_row.setdefault("msg", []).append(
					_("Cashier doesn't match {}").format(frappe.bold(self.cashier))
				)

			if invalid_row.get("msg"):
				invalid_rows.append(invalid_row)

		if not invalid_rows:
			return

		error_list = []
		for row in invalid_rows:
			for msg in row.get("msg"):
				error_list.append(_("Row #{}: {}").format(row.get("idx"), msg))

		frappe.throw(error_list, title=_("Invalid Reference"), as_list=True)

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
		for d in self.get("payments"):
			account = get_bank_cash_account(d.mode_of_payment, self.company)
			accounts.append({
				"account": account,
				"debit_in_account_currency": flt(d.amount),
				"cost_center": self.cost_center,
				"reference_type": self.doctype,
				"reference_name": self.name,
			})

		accounts.append({
			"account": income_account,
			"credit_in_account_currency": flt(self.grand_total),
			"cost_center": self.cost_center,
		})

		je = frappe.new_doc("Journal Entry")
		
		voucher_type = "Journal Entry"
		naming_series = "Journal Voucher"
		
		je.update({
				"doctype": "Journal Entry",
				"voucher_type": voucher_type,
				"naming_series": naming_series,
				"title": "Entry Fee - "+self.location,
				"user_remark": "Entry Fee - "+self.location,
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

@frappe.whitelist()
def get_reference_document(date, location, cashier):
	try:
		data = frappe.db.sql("""
			SELECT name, posting_date
			FROM `tabVisitor Pass Registry`
			WHERE cashier = %s 
				AND location = %s 
				AND docstatus = 1 
				AND posting_date = %s
				AND status = 'Open'
		""", (cashier, location, date), as_dict=1)

		data = [frappe.get_doc("Visitor Pass Registry", d.name).as_dict() for d in data]
		return data
	except Exception as e:
		frappe.log_error(f"Error in get_reference_document: {e}")
		return []
