# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ProductionAccountSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		company: DF.Link
		default_production_account: DF.Link
		default_royalty_account: DF.Link
		discount_account: DF.Link | None
		transportation_account: DF.Link | None
	# end: auto-generated types
	def on_update(self):
		self.check_duplicate()

	def check_duplicate(self):
		for a in frappe.db.sql("select name from `tabProduction Account Settings` where company = %s and name != %s", (self.company, self.name), as_dict=1):
			frappe.throw("Production Account Settings already created for your Company")

