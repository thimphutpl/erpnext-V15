# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HiringRequestDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		equipment_type: DF.Link
		from_date: DF.Date
		location: DF.Data | None
		number_of_days: DF.Data | None
		number_of_hours: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		remarks: DF.SmallText | None
		to_date: DF.Date
	# end: auto-generated types
	pass
