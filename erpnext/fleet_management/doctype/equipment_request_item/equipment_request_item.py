# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EquipmentRequestItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		approved: DF.Check
		approved_qty: DF.Data | None
		equipment_type: DF.Link
		from_date: DF.Date
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		percent_share: DF.Percent
		place: DF.Data
		qty: DF.Data
		rate_type: DF.Literal["", "With Fuel", "Without Fuel"]
		reason: DF.Text | None
		to_date: DF.Date
		total_hours: DF.Float
	# end: auto-generated types
	pass
