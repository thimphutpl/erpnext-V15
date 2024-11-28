# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ExtensionofTime(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		eot_in_days: DF.Int
		expected_end_date: DF.Date | None
		expected_start_date: DF.Date | None
		extended_end_date: DF.Date
		extension_order: DF.Attach | None
		projects: DF.Link
		reason_for_extension: DF.TextEditor | None
	# end: auto-generated types
	pass
