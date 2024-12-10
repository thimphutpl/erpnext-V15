# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FunctionalUnitTargets(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		deadline: DF.Literal["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
		key_performance_indicators: DF.Data | None
		key_result_areas: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		perspectives: DF.Link | None
		target: DF.Data | None
		weightage: DF.Percent
	# end: auto-generated types
	pass
