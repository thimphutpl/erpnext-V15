# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class POLReceiveItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		date: DF.Date | None
		item_code: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		qty: DF.Float
		rate: DF.Currency
		remarks: DF.SmallText | None
		site: DF.Data | None
		supply_memo: DF.Data | None
		uom: DF.Link | None
		vehicle_number: DF.Data | None
	# end: auto-generated types
	pass
