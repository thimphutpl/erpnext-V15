# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class POLAdvanceItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		advance_amount: DF.Currency
		advance_balance: DF.Currency
		allocated_amount: DF.Currency
		amount: DF.Currency
		balance: DF.Currency
		has_od: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		reference: DF.Link | None
	# end: auto-generated types
	pass
