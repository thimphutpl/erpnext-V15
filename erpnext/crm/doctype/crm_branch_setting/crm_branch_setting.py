# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
import re


class CRMBranchSetting(Document):
    def autoname(self):
        # Replace disallowed characters with '-' (or remove them)
        branch_clean = re.sub(r'[^\w\s-]', '', self.branch or "")
        product_clean = re.sub(r'[^\w\s-]', '', self.product_category or "")
        
        # Base name
        base_name = f"{branch_clean} - {product_clean}"

        if frappe.db.exists("CRM Branch Setting", base_name):
            # If exists, add series numbering
            self.name = make_autoname(f"{branch_clean} - {product_clean} .####")
        else:
            self.name = base_name
