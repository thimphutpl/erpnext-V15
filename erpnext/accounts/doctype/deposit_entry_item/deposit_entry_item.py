# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DepositEntryItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		cash_amount: DF.Currency
		cashier: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		pos_closing_entry: DF.Link | None
		posting_date: DF.Date | None
	# end: auto-generated types
	pass
