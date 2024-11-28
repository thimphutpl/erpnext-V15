# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LeadershipCompetencyI(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		achievement: DF.Link | None
		average: DF.Float
		competency: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		rating: DF.Rating
		remarks: DF.Text | None
		weightage: DF.Data
		weightage_percent: DF.Literal["10", "20", "30", "40", "50", "60", "70", "80", "90", "100"]
	# end: auto-generated types
	pass
