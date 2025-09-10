# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MonthlyIndent(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF


	# end: auto-generated types
	def validate(self):	
		pass

	def on_submit(self):
		if not self.status == 'Completed':
			frappe.throw("Only Completed Monthly Indent can be Submitted.") 

