# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BudgetActivity(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from erpnext.budget.doctype.sub_actvity_list.sub_actvity_list import SubActvityList
        from frappe.types import DF

        abbr: DF.Data
        activity_code: DF.Data
        activity_name: DF.Data
        company: DF.Link
        disabled: DF.Check
        table_rllq: DF.Table[SubActvityList]
    # end: auto-generated types

    def autoname(self):
        # frappe.throw("here")
        self.name = self.activity_code + " - " + self.activity_name + " - " + self.abbr
