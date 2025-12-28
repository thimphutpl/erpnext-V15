# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LotAllotmentLots(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		additional: DF.Currency
		discount: DF.Currency
		lot_number: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		payable_amount: DF.Currency
		pieces: DF.Int
		total_amount: DF.Currency
		total_volume: DF.ReadOnly | None
	# end: auto-generated types
	pass
