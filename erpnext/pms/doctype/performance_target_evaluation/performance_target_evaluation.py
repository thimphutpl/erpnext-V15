# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class PerformanceTargetEvaluation(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.SmallText
		from_date: DF.Date
		main_activities: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		performance_target: DF.Data
		to_date: DF.Date
		weightage: DF.Float
	# end: auto-generated types
	pass
