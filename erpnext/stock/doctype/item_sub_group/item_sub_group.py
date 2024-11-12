# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ItemSubGroup(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		disabled: DF.Check
		item_code_base: DF.Data
		item_group: DF.Link
		item_sub_group: DF.Data
	# end: auto-generated types
	pass

	def before_save(self):
		if not self.item_code_base:
			frappe.throw(f"Missing Item Code Base")
		if len(self.item_code_base) != 3:
			frappe.throw(f"Length of Item Code Base has to be 3")