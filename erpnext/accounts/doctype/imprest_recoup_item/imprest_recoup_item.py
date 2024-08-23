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
		cost_center: DF.Link
		invoice_date: DF.Date
		invoice_no: DF.Data
		name: DF.Int | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		recoup_type: DF.Link | None
		reference_name: DF.DynamicLink | None
		reference_type: DF.Link | None
		remarks: DF.SmallText | None
	# end: auto-generated types
	pass
