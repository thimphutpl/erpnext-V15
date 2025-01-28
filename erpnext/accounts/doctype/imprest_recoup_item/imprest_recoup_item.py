# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class ImprestRecoupItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link
		amount: DF.Currency
		business_activity: DF.Link
		invoice_date: DF.Date
		invoice_no: DF.Data | None
		item_code: DF.Link | None
		item_name: DF.Data | None
		maintain_stock: DF.Check
		name: DF.Int | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		project: DF.Link | None
		quantity: DF.Float
		rate: DF.Data
		reference_name: DF.DynamicLink | None
		reference_type: DF.Link | None
		remarks: DF.SmallText | None
		uom: DF.Link | None
	# end: auto-generated types
	pass
