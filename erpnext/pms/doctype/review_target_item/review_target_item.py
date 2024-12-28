# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class ReviewTargetItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		appraisees_remarks: DF.SmallText | None
		appraisers_remarks: DF.SmallText | None
		description: DF.SmallText | None
		from_date: DF.Date | None
		main_activities: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		performance_target: DF.Data | None
		to_date: DF.Date | None
		weightage: DF.Percent
	# end: auto-generated types
	pass
