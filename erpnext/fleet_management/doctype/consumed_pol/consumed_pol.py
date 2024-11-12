# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ConsumedPOL(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		company: DF.Link
		date: DF.Date
		equipment: DF.Link
		pol_type: DF.Data
		qty: DF.Float
		reference_name: DF.DynamicLink | None
		reference_type: DF.Literal["", "POL", "Issue POL", "Equipment POL Transfer"]
	# end: auto-generated types
	pass
