# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class AssetOthers(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.assets.doctype.asset_parts.asset_parts import AssetParts
		from frappe.types import DF

		additional_value: DF.Currency
		asset_category: DF.Link | None
		asset_name: DF.Data
		branch: DF.Link
		brand: DF.Data | None
		company: DF.Link | None
		contact_details: DF.Data | None
		custodian: DF.Link | None
		employee_name: DF.Data | None
		from_date: DF.Date
		gross_purchase_amount: DF.Currency
		is_existing_asset: DF.Check
		model: DF.Data | None
		old_asset_id: DF.Data | None
		owned_by: DF.Link
		part_items: DF.Table[AssetParts]
		serial_number: DF.Data | None
		status: DF.Literal["In-Use", "Returned", "Damaged"]
		to_date: DF.Date | None
	# end: auto-generated types
	# end: auto-generated types
	def autoname(self):
			if self.old_asset_code:
				self.name = self.old_asset_code
