# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MAXitem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		activity: DF.Data | None
		area: DF.Data | None
		baseline: DF.Data | None
		key_result_areas: DF.Data | None
		kpi: DF.Data
		output: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		self_rating: DF.Data | None
		supervisor_rating: DF.Data | None
	# end: auto-generated types
	pass
