# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Equipment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.equipment_operator_item.equipment_operator_item import EquipmentOperatorItem
		from frappe.types import DF

		asset_code: DF.Link | None
		branch: DF.Link
		category: DF.Link
		chasis_number: DF.Data | None
		company: DF.Link
		cost_center: DF.Link | None
		disabled: DF.Check
		engine_number: DF.Data | None
		equipment_name: DF.Data | None
		fuel_type: DF.Link | None
		fuelbook: DF.Link | None
		initial_reading: DF.Float
		model: DF.Data
		reading_uom: DF.Link | None
		registration_number: DF.Data
		table_qptk: DF.Table[EquipmentOperatorItem]
		type: DF.Link
	# end: auto-generated types
	pass
