# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class OverallRating(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		lower_range: DF.Float
		lower_range_percent: DF.Percent
		rating: DF.Data
		star: DF.Rating
		upper_range: DF.Float
		upper_range_percent: DF.Percent
		weightage: DF.Literal["", "100", "90", "80", "70", "60", "50", "40", "30", "20", "10"]
	# end: auto-generated types
	def validate(self):
		# self.star = self.weightage
		pass
