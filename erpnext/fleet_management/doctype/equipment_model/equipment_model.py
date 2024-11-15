# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class EquipmentModel(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_form: DF.Link | None
		equipment_type: DF.Link
		model: DF.Data
		registeration_number: DF.Data
		tank_capacity: DF.Data | None
	# end: auto-generated types
	def autoname(self):
		self.name = self.equipment_type + "(" + self.model + ")"
