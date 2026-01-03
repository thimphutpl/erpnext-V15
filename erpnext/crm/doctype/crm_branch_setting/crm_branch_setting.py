# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document


class CRMBranchSetting(Document):
	def autoname(self):
		self.name = self.branch+" ("+self.product_category+")"
		if frappe.db.exists("CRM Branch Setting",self.name):
			self.name = make_autoname(self.branch+" ("+self.product_category+ ") .####")
