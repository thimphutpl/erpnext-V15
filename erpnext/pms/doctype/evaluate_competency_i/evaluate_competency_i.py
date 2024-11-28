# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EvaluateCompetencyI(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		achievement: DF.Link | None
		appraisees_remark: DF.SmallText | None
		appraisers_remark: DF.SmallText | None
		average: DF.Float
		comment: DF.SmallText | None
		competency: DF.Link | None
		description: DF.SmallText | None
		is_parent: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		rating: DF.Rating
		score: DF.Float
		self_rating: DF.Float
		sub_competency: DF.Data | None
		supervisor_rating: DF.Float
		top_level: DF.Data | None
		weightage: DF.Data | None
		weightage_percent: DF.Literal["10", "20", "30", "40", "50", "60", "70", "80", "90", "100"]
		work_competency_id: DF.Link | None
	# end: auto-generated types
	pass
