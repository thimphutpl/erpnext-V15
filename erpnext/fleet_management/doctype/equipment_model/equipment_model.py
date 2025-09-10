# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EquipmentModel(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		disabled: DF.Check
		equipment_type: DF.Link
		model: DF.Data
	# end: auto-generated types
	# def autoname(self):
	# 	self.name = self.equipment_type + "(" + self.model + ")" 

	def autoname(self):
		self.name = self.model
	
