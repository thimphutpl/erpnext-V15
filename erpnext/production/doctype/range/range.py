# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Range(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.production.doctype.range_location.range_location import RangeLocation
		from frappe.types import DF

		branch: DF.Link | None
		company: DF.Link
		is_disabled: DF.Check
		items: DF.Table[RangeLocation]
		location: DF.Link | None
		range_name: DF.Data | None
	# end: auto-generated types
	pass
