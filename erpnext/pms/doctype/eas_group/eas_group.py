# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EASGroup(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		group_name: DF.Data
		negative_target: DF.Check
		required_to_set_target: DF.Check
		weightage_for_competency: DF.Percent
		weightage_for_target: DF.Percent
	# end: auto-generated types
	pass
