# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DirectPaymentItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link
		amount: DF.Currency
		invoice_date: DF.Date | None
		invoice_no: DF.Data | None
		net_amount: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		party: DF.DynamicLink | None
		party_type: DF.Literal["", "Supplier", "Customer", "Employee"]
		project: DF.Link | None
		sundry_account: DF.Link | None
		taxable_amount: DF.Currency
		tds_amount: DF.Currency
		tds_applicable: DF.Check
	# end: auto-generated types
	pass
