# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class PMSGroup(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.Data | None
		group_name: DF.Data
		negative_target: DF.Check
		required_activity: DF.Check
		required_aligned_to_3_spec: DF.Check
		required_area: DF.Check
		required_baselined: DF.Check
		required_key_result_areas: DF.Check
		required_to_set_target: DF.Check
		weightage_for_competency: DF.Data
		weightage_for_target: DF.Data
	# end: auto-generated types
	pass
