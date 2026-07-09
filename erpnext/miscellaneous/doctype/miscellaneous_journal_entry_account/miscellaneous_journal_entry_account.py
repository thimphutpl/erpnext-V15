# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MiscellaneousJournalEntryAccount(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link
		account_currency: DF.Link | None
		account_type: DF.Data | None
		actual_amount: DF.Currency
		advance_settlement_id: DF.Data | None
		against_account: DF.Text | None
		balance: DF.Currency
		bank_account: DF.Link | None
		beneficiary: DF.DynamicLink | None
		beneficiary_type: DF.Link | None
		cost_center: DF.Link | None
		credit: DF.Currency
		debit: DF.Currency
		is_advance: DF.Literal["No", "Yes"]
		is_opening_adjustment: DF.Check
		is_settlement: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		party: DF.DynamicLink | None
		party_balance: DF.Currency
		party_check: DF.Check
		party_name: DF.Data | None
		party_type: DF.Link | None
		reference_due_date: DF.Date | None
		reference_name: DF.DynamicLink | None
		reference_type: DF.Literal["", "Contribution Refund", "Investment", "Loan", "Semso Application", "SWS Journal Entry"]
		user_remark: DF.SmallText | None
	# end: auto-generated types

	pass
