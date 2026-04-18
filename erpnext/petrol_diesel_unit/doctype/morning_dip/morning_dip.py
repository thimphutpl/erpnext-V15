# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MorningDip(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		current_stock_balance: DF.Float
		current_stock_value: DF.Currency
		previous_stock_balance: DF.Float
		previous_stock_value: DF.Currency
	# end: auto-generated types
	pass
