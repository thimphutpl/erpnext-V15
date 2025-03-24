# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class VisitorPassOtherCharges(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		fee_type: DF.Link
		journal_no: DF.Data | None
		mode_of_payment: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		qty: DF.Int
		rate: DF.Currency
		remarks: DF.SmallText | None
	# end: auto-generated types
	pass
