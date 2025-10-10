# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AppraisalPeriod(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		appraisal_period: DF.Data
		evaluation_end_date: DF.Date
		evaluation_start_date: DF.Date
		planning_end_date: DF.Date
		planning_start_date: DF.Date
	# end: auto-generated types
	pass
