# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class VisitorPassRegistryItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		journal_no: DF.Data | None
		mode_of_payment: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		qty: DF.Int
		remarks: DF.SmallText | None
		ticket_price: DF.Currency
		ticket_type: DF.Link
	# end: auto-generated types
	pass
