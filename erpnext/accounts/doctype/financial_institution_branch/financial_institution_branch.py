# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FinancialInstitutionBranch(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		branch_name: DF.Data
		financial_institution: DF.Link
		financial_system_code: DF.Data
		short_form: DF.Data | None
	# end: auto-generated types
	
	def autoname(self):
		self.name = " - ".join([self.branch_name,str(self.financial_institution).strip()])
