# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProductionGroup(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.production.doctype.production_group_item.production_group_item import ProductionGroupItem
		from frappe.types import DF

		items: DF.Table[ProductionGroupItem]
		production_group: DF.Data
	# end: auto-generated types
	pass
