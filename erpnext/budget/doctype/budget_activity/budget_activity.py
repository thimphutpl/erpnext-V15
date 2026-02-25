# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BudgetActivity(Document):
    def autoname(self):
        # frappe.throw("here")
        self.name = self.activity_code + " - " + self.activity_name
