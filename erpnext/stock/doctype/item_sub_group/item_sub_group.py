# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ItemSubGroup(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.stock.doctype.item_sub_group_measurement.item_sub_group_measurement import ItemSubGroupMeasurement
		from frappe.types import DF

		is_crm_item: DF.Check
		is_vehicle: DF.Check
		item_group: DF.Link
		item_sub_group: DF.Data
		items: DF.Table[ItemSubGroupMeasurement]
		lot_check: DF.Check
		maximum_value: DF.Float
		minimum_value: DF.Float
		reading_parameter: DF.Data | None
		reading_required: DF.Check
		uom: DF.Link | None
	# end: auto-generated types
	def validate(self):
		if self.reading_required:
			if not self.reading_parameter:
				frappe.throw("Reading Parameter is Mandatory")
			if flt(self.minimum_value) > flt(self.maximum_value):
				frappe.throw("Invalid Min and Max Acceptable Values")