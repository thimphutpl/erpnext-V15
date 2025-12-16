# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class OrderConfirmationDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		advance__remarks: DF.SmallText | None
		advances_paid: DF.Currency
		amount: DF.Currency
		discount_amount: DF.Currency
		gross_price: DF.Currency
		item_code: DF.Link
		item_details: DF.LongText | None
		item_name: DF.Data | None
		net_price: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		quantity: DF.Data | None
	# end: auto-generated types
	pass
