# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MiscellaneousJournalEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.miscellaneous.doctype.miscellaneous_journal_entry_account.miscellaneous_journal_entry_account import MiscellaneousJournalEntryAccount
		from frappe.types import DF

		accounts: DF.Table[MiscellaneousJournalEntryAccount]
		amended_from: DF.Link | None
		auto_repeat: DF.Link | None
		bank_payment: DF.Link | None
		bill_date: DF.Date | None
		bill_no: DF.Data | None
		branch: DF.Link | None
		cheque_date: DF.Date | None
		cheque_no: DF.Data | None
		clearance_date: DF.Date | None
		company: DF.Link
		currency: DF.Link
		difference: DF.Currency
		due_date: DF.Date | None
		inter_company_journal_entry_reference: DF.Link | None
		is_opening: DF.Literal["No", "Yes"]
		letter_head: DF.Link | None
		mode_of_payment: DF.Link | None
		naming_series: DF.Literal["Journal Voucher", "Bank Payment Voucher", "Bank Receipt Voucher", "Cash Receipt Voucher", "Cash Payment Voucher", "Contra Entry", "Initial Upload"]
		paid_loan: DF.Data | None
		pay_to_recd_from: DF.Data | None
		payment_order: DF.Link | None
		payment_status: DF.Data | None
		posting_date: DF.Date
		reference_name: DF.DynamicLink | None
		reference_type: DF.Link | None
		remark: DF.SmallText | None
		select_cheque_lot: DF.Link | None
		select_print_heading: DF.Link | None
		stock_entry: DF.Link | None
		title: DF.Data | None
		total_amount: DF.Currency
		total_amount_currency: DF.Link | None
		total_amount_in_words: DF.Data | None
		total_credit: DF.Currency
		total_debit: DF.Currency
		use_cheque_lot: DF.Check
		user_remark: DF.SmallText | None
		voucher_type: DF.Literal["Journal Entry", "Bank Entry", "Cash Entry", "Opening Entry"]
		write_off_amount: DF.Currency
		write_off_based_on: DF.Literal["Accounts Receivable", "Accounts Payable"]
	# end: auto-generated types

	pass
