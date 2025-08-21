# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MaterialReturnItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		basic_rate: DF.Currency
		expense_account: DF.Link | None
		item_code: DF.Link
		item_group: DF.Data | None
		item_name: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		project: DF.Link | None
		qty: DF.Float
		remarks: DF.SmallText | None
		stock_uom: DF.Data | None
		valuation_rate: DF.Currency
		warehouse: DF.Link
	# end: auto-generated types
	pass
