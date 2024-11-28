# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class EquipmentType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		equipment_category: DF.Link
		equipment_type: DF.Data
		is_container: DF.Check
		no_own_tank: DF.Check
	# end: auto-generated types
	pass
