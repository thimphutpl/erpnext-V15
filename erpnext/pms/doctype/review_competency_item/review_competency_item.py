# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class ReviewCompetencyItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		appraisees_remark: DF.SmallText | None
		appraisers_remark: DF.SmallText | None
		competency: DF.Data | None
		description: DF.SmallText | None
		is_parent: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		sub_competency: DF.Data | None
		weightage: DF.Data | None
	# end: auto-generated types
	pass
