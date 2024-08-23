# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class PMSSetting(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		approver: DF.Link | None
		approver_designation: DF.Data | None
		approver_id: DF.Link | None
		approver_name: DF.Data | None
		max_rating_limit: DF.Literal["", "100", "90", "80", "70"]
		max_weightage_for_target: DF.Float
		min_weightage_for_target: DF.Float
	# end: auto-generated types
	pass
