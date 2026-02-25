# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BudgetSubActivity(Document):
	def autoname(self):
		self.name = self.sub_activity_code+" - " + self.sub_activity_name
