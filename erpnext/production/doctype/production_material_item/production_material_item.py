# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProductionMaterialItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		actual_qty: DF.Float
		business_activity: DF.Link | None
		cost_center: DF.Link | None
		cull_qty: DF.Float
		cull_qty_file: DF.Attach | None
		expense_account: DF.Link | None
		item_code: DF.Link
		item_name: DF.Data
		lot_list: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		qty: DF.Float
		uom: DF.Link
		warehouse: DF.Link | None
	# end: auto-generated types
	pass
