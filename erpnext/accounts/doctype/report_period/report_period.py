# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ReportPeriod(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		c_from_date: DF.Data
		c_to_date: DF.Data
		from_date: DF.Data
		name_period: DF.Data
		order: DF.Data
		to_date: DF.Data
	# end: auto-generated types
	pass
