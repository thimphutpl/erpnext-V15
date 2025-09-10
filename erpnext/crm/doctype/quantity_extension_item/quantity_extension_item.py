# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class QuantityExtensionItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		additional_quantity: DF.Float
		branch: DF.Link | None
		distance: DF.Float
		final_quantity: DF.Float
		initial_quantity: DF.Float
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		product_category: DF.Link
		remarks: DF.SmallText | None
		site_item_name: DF.Data | None
		transport_mode: DF.Literal["", "Self Owned Transport", "Common Pool"]
		transportation_rate: DF.Currency
		unit_rate: DF.Currency
		uom: DF.ReadOnly | None
	# end: auto-generated types
	pass
