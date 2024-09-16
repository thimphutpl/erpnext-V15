# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SoelraDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		currency: DF.Link | None
		estimated_fair_market_value: DF.Currency
		estimated_fair_market_valuenu: DF.Currency
		exchange_rate: DF.Float
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		particulars: DF.Link | None
		quantity: DF.Int
		rate: DF.Currency
		uom: DF.Data | None
		warehouse: DF.Link | None
	# end: auto-generated types
	pass
