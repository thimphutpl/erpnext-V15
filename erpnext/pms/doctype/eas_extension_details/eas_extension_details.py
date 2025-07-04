# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EASExtensionDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		appeal_end_date: DF.Date | None
		appeal_start_date: DF.Date
		eas_group: DF.Link
		evaluation_end_date: DF.Date
		evaluation_start_date: DF.Date
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		review_end_date: DF.Date | None
		review_start_date: DF.Date
		target_end_date: DF.Date
		target_start_date: DF.Date
	# end: auto-generated types
	pass
