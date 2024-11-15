# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


# import frappe
from frappe.model.document import Document


class AssetMovementItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		asset: DF.Link
		asset_name: DF.Data | None
		company: DF.Link | None
		from_employee: DF.Link | None
		from_employee_name: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		source_cost_center: DF.Link | None
		target_cost_center: DF.Link | None
		to_employee: DF.Link | None
		to_employee_name: DF.Data | None
	# end: auto-generated types

	pass
