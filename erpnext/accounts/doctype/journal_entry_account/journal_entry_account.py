# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt


from frappe.model.document import Document


class JournalEntryAccount(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link
		account_currency: DF.Link | None
		account_type: DF.Data | None
		add_deduct_tax: DF.Literal["", "Add", "Deduct"]
		against_account: DF.Text | None
		apply_tds: DF.Check
		bank_account: DF.Link | None
		bill_date: DF.Date | None
		bill_no: DF.Data | None
		business_activity: DF.Link | None
		cost_center: DF.Link | None
		credit: DF.Currency
		credit_in_account_currency: DF.Currency
		debit: DF.Currency
		debit_in_account_currency: DF.Currency
		exchange_rate: DF.Float
		is_advance: DF.Literal["No", "Yes"]
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		party: DF.DynamicLink | None
		party_type: DF.Link | None
		project: DF.Link | None
		rate: DF.Float
		reference_detail_no: DF.Data | None
		reference_due_date: DF.Date | None
		reference_name: DF.DynamicLink | None
		reference_type: DF.Literal["", "Bonus", "PBVA", "Sales Invoice", "SWS Application", "Purchase Invoice", "Journal Entry", "Sales Order", "Purchase Order", "Expense Claim", "Asset", "Loan", "Payroll Entry", "Employee Advance", "Exchange Rate Revaluation", "Invoice Discounting", "Fees", "Full and Final Statement", "Payment Entry", "Abstract Bill", "Imprest Advance", "Imprest Recoup", "POL Advance", "Process MR Payment", "Travel Claim", "Travel Authorization", "Fund Requisition", "Leave Encashment", "Bulk Leave Encashment", "Leave Travel Concession", "Equipment Hiring Form", "Job Cards", "Employee Benefits"]
		tax_account: DF.Link | None
		tax_amount: DF.Currency
		tax_amount_in_account_currency: DF.Currency
		taxable_amount: DF.Currency
		taxable_amount_in_account_currency: DF.Currency
		user_remark: DF.SmallText | None
	# end: auto-generated types

	pass
