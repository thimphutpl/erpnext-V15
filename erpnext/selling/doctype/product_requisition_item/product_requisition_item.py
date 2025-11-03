# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProductRequisitionItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		balance: DF.Float
		item_code: DF.Link | None
		item_name: DF.ReadOnly | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		qty: DF.Float
		qty_required: DF.Float
		uom: DF.ReadOnly | None
	# end: auto-generated types
	pass
