# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from frappe import _
from frappe.utils import flt


class CashDepositEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.event_management.doctype.cash_deposit_entry_item.cash_deposit_entry_item import CashDepositEntryItem
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		company: DF.Link | None
		cost_center: DF.Link | None
		from_date: DF.Date | None
		items: DF.Table[CashDepositEntryItem]
		journal_entry: DF.Data | None
		location: DF.Link
		posting_date: DF.Date | None
		to_date: DF.Date | None
	# end: auto-generated types
	pass

	def post_cash_entry(self):
		cash_account = frappe.db.get_value("Company", self.company, "default_cash_account")
		bank_account = frappe.db.get_value("Company", self.company, "default_bank_account")

		if not cash_account:
			frappe.throw(
				"Default Bank Account is not set for {}. Please configure it in the company.".format(
					frappe.get_desk_link("Company", self.company)
				),
				title="Missing Account"
			)

		if not bank_account:
			frappe.throw(
				"Default Bank Account is not set for {}. Please configure it in the company.".format(
					frappe.get_desk_link("Company", self.company)
				),
				title="Missing Account"
			)

		# Posting Journal Entry
		accounts = []
		accounts.append({
			"account": bank_account,
			"debit_in_account_currency": flt(self.cash_amount),
			"cost_center": self.cost_center,
			"reference_type": self.doctype,
			"reference_name": self.name,
		})

		accounts.append({
			"account": cash_account,
			"credit_in_account_currency": flt(self.cash_amount),
			"cost_center": self.cost_center,
		})

		je = frappe.new_doc("Journal Entry")
		
		voucher_type = "Journal Entry"
		naming_series = "Journal Voucher"
		
		je.update({
				"doctype": "Journal Entry",
				"voucher_type": voucher_type,
				"naming_series": naming_series,
				"title": "Bank to Cash - "+self.location,
				"user_remark": "Bank to cash - "+self.location,
				"posting_date": self.posting_date,
				"company": self.company,
				"accounts": accounts,
				"branch": self.branch
		})

		je.save(ignore_permissions = True)
