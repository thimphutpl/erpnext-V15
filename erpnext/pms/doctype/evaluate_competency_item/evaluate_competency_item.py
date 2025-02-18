# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class EvaluateCompetencyItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		appraisees_remark: DF.SmallText | None
		appraisers_remark: DF.SmallText | None
		competency: DF.Link | None
		description: DF.SmallText | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		remarks: DF.SmallText | None
		self_rating: DF.Float
		supervisor_rating: DF.Float
		weightage: DF.Data | None
	# end: auto-generated types
	pass
