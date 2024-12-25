# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint, flt, nowdate, money_in_words


class CompactReview(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.compact_agreement.doctype.compact_agreement_items_review.compact_agreement_items_review import CompactAgreementItemsReview
		from frappe.types import DF

		agency: DF.Link
		amended_from: DF.Link | None
		company: DF.Link
		fiscal_year: DF.Link
		table_uflv: DF.Table[CompactAgreementItemsReview]
	# end: auto-generated types

def before_save(self):
        """Save data of Compact Review within the Compact Review doctype."""
        self.last_updated = nowdate()
        frappe.msgprint("Compact Review data has been saved successfully.")

def before_print(self, settings=None):
        """Use the first suppliers data to render the print preview."""
        if self.vendor or not self.suppliers:
            return

        self.update_supplier_part_no(self.suppliers[0].supplier)

def on_cancel(self):
        self.db_set("status", "Cancelled")
        
def group_items_by_output(self):
        """Group items based on 'output' checkbox in child table."""
        groups = []
        current_group = []

        for item in self.table_vaeg:
            if item.output:
                if current_group:
                    groups.append(current_group)
                current_group = [item]
            else:
                current_group.append(item)

        if current_group:
            groups.append(current_group)

        return groups

def get_group_for_item(self, item_to_delete):
        """Find the group that contains the item to delete."""
        grouped_items = self.group_items_by_output()

        for group in grouped_items:
            if item_to_delete in group:
                return group
        return []

def before_delete(self, item_to_delete):
        """Delete the entire group when the checked output item is deleted."""
        if item_to_delete.output:
            group = self.get_group_for_item(item_to_delete)
            for item in group:
                item.delete()
        else:
            item_to_delete.delete()

def on_trash(self):
        """Override the trash method to ensure group deletion works."""
        for item in self.table_vaeg:
            self.before_delete(item)	           			
   
@frappe.whitelist()
def make_compact_evaluation(source_name, target_doc=None): 
    def update_date(obj, target, source_parent):
        target.posting_date = nowdate()

    doc = get_mapped_doc("Compact Review", source_name, {
        "Compact Review": {
            "doctype": "Compact Evaluation",
            "field_map": {
                "name": "compact_evaluation",
                "date": "compact_review_date"
            },
            "postprocess": update_date, 
        },
        "Compact Agreement Items Review": {  
            "doctype": "Compact Agreement Items Evaluation", 
            "field_map": {
                "target": "target",     
                "deliverables": "deliverables",
                "deadlines": "deadlines",
                "weighted": "weighted",
                "remarks": "remarks"
            }
        }
    }, target_doc)
    
    return doc
