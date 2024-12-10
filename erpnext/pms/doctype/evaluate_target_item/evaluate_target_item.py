# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class EvaluateTargetItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		accept_zero_qtyquality: DF.Check
		appraisees_remarks: DF.SmallText | None
		appraisers_remark: DF.SmallText | None
		average_rating: DF.Float
		comment: DF.SmallText | None
		description: DF.SmallText | None
		employee_remarks: DF.Text | None
		from_date: DF.Date | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		performance_target: DF.Data | None
		qty_quality: DF.Literal["", "Quantity", "Quality"]
		quality: DF.Percent
		quality_achieved: DF.Float
		quality_rating: DF.Float
		quantity: DF.Float
		quantity_achieved: DF.Float
		quantity_rating: DF.Float
		reverse_formula: DF.Check
		score: DF.Percent
		self_rating: DF.Float
		supervisor_rating: DF.Float
		supervisor_remarks: DF.Text | None
		timeline_achieved: DF.Percent
		timeline_rating: DF.Float
		to_date: DF.Date | None
		weightage: DF.Float
	# end: auto-generated types
	pass
