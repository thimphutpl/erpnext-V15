# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BudgetSubActivity(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		abbr: DF.Data | None
		company: DF.Link
		sub_activity_code: DF.Data
		sub_activity_name: DF.Data
	# end: auto-generated types

	def autoname(self):
		self.name = self.sub_activity_code+" - " + self.sub_activity_name + " - " + self.abbr
