# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ItemSubGroup(Document):
	def validate(self):
		if self.reading_required:
			if not self.reading_parameter:
				frappe.throw("Reading Parameter is Mandatory")
			if flt(self.minimum_value) > flt(self.maximum_value):
				frappe.throw("Invalid Min and Max Acceptable Values")