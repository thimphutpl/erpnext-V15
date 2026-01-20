# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ConsolidatedInvoiceItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		accepted_qty: DF.Float
		amount: DF.Currency
		challan_cost: DF.Currency
		cost_of_goods: DF.Currency
		date: DF.Date
		delivery_note: DF.Link
		discount_amount: DF.Currency
		due_date: DF.Date
		gst_amount: DF.Currency
		invoice_no: DF.Link
		loading_cost: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		qty: DF.Float
		sales_order: DF.Link
		transportation_cost: DF.Currency
	# end: auto-generated types
	pass
