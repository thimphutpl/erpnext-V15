# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProductCategoryItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		item_group: DF.ReadOnly | None
		item_sub_group: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		product_group: DF.Link | None
		selection_based_on: DF.ReadOnly
		use_product_group: DF.Check
	# end: auto-generated types
	pass
