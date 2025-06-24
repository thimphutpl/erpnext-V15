# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BankPaymentItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		bank_account_no: DF.Data | None
		bank_account_type: DF.Data | None
		bank_branch: DF.Link | None
		bank_journal_no: DF.Data | None
		bank_name: DF.Link | None
		beneficiary_name: DF.Data | None
		customer: DF.Link | None
		employee: DF.Link | None
		error_message: DF.Code | None
		file_name: DF.Data | None
		financial_system_code: DF.Data | None
		inr_bank_code: DF.Literal["", "01 - AXIS BANK", "02- SBI", "03 -Others", "04 - SCB"]
		inr_purpose_code: DF.Literal["", "01- INVT IN EQUITY SHARE", "02- INVT IN MUTUAL FUND", "03- INVT IN DEBENTURES", "04- BILL PAYMENT", "05- CREDIT TO NRE A/c", "06- PAYMENT TO HOTELS", "07- TRAVEL & TOURISM", "08- INVT IN REAL ESTATE", "09- PYMNT TO ESTATE DEVELOPER", "10- LIC PREMIUM", "11- EDUCATIONAL EXPENSES", "12- FAMILY MAINTENANCE", "13- POSTMASTER / UTI PREMIUM", "14- PROPERTY Pymnt-Co-op Hsg.Soc", "15- PROPERTY Pymnt-Govt. Hsg.Scheme", "16- MEDICAL EXPENSES", "17- UTILITY PAYMENTS", "18- TAX PAYMENTS", "19- EMI FOR LOAN REPAYMENT", "20- COMPENSATION OF EMPLOYEES", "21- SALARY"]
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		pi_number: DF.Data | None
		remarks: DF.SmallText | None
		status: DF.Literal["", "Draft", "Pending", "In progress", "Upload Failed", "Waiting Acknowledgement", "Processing Acknowledgement", "Failed", "Partial Payment", "Completed", "Cancelled"]
		supplier: DF.Link | None
		transaction_date: DF.Date | None
		transaction_id: DF.DynamicLink
		transaction_reference: DF.Data | None
		transaction_type: DF.Link | None
		vehicle_no: DF.Data | None
	# end: auto-generated types
	pass
