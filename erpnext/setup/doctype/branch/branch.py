# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from frappe.model.document import Document
import frappe
import re


class Branch(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		abbreviation: DF.Data | None
		branch: DF.Data
		company: DF.Link
		cost_center: DF.Link
		disabled: DF.Check
		expense_bank_account: DF.Link | None
		holiday_list: DF.Link | None
	# end: auto-generated types

	def validate(self):
		if not self.get("__islocal"):
			self.validate_branch_abbreviation()

	def validate_branch_abbreviation(self):
		if not self.abbreviation:
			frappe.throw("Please set Abbreviation for this branch")
		# if not re.match(r'^[A-Z]{3}$', self.abbreviation):
		# 	frappe.throw("Branch abbreviation must be exactly three uppercase alphabet letters")
