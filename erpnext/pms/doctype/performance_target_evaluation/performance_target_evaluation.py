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

		description: DF.SmallText | None
		from_date: DF.Date | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		performance_target: DF.Data
		qty_quality: DF.Literal["", "Quantity", "Quality"]
		quality: DF.Percent
		quantity: DF.Float
		reverse_formula: DF.Check
		to_date: DF.Date | None
		weightage: DF.Float
	# end: auto-generated types
	pass
