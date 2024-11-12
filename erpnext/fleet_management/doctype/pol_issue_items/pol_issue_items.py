# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class POLIssueItems(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		cost_center: DF.Link | None
		cur_km_reading: DF.Float
		equipment: DF.Link
		equipment_category: DF.Link | None
		fuel_book_branch: DF.Link | None
		fuel_cost_center: DF.Link | None
		fuelbook: DF.Link
		item_code: DF.Link | None
		km_difference: DF.Float
		mileage: DF.Float
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		previous_km: DF.Float
		project: DF.Link | None
		qty: DF.Float
		rate: DF.Currency
		stock_uom: DF.Link | None
		uom: DF.Literal["", "Hour", "KM"]
		warehouse: DF.Link | None
	# end: auto-generated types
	pass
