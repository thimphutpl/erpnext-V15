# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint, flt, nowdate, money_in_words


class CompactEvaluation(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.compact_agreement.doctype.compact_agreement_items_evaluation.compact_agreement_items_evaluation import CompactAgreementItemsEvaluation
		from frappe.types import DF

		agency: DF.Link
		amended_from: DF.Link | None
		company: DF.Link
		fiscal_year: DF.Link
		table_qwvz: DF.Table[CompactAgreementItemsEvaluation]
		total_achieved_percent: DF.Percent
		total_weighted_percent: DF.Percent
	# end: auto-generated types

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.compact_agreement.doctype.compact_agreement_items_evaluation.compact_agreement_items_evaluation import CompactAgreementItemsEvaluation
		from frappe.types import DF

		agency: DF.Link | None
		amended_from: DF.Link | None
		company: DF.Link | None
		fiscal_year: DF.Link | None
		table_qwvz: DF.Table[CompactAgreementItemsEvaluation]

# def before_save(self):
#         """Save data of Compact Evaluation within the Compact Evaluation doctype."""
#         self.last_updated = nowdate()
#         frappe.msgprint("Compact Evaluation data has been saved successfully.")

def before_save(self):
        """Calculate totals for 'weighted' and 'achieved' and store as percent."""
        total_weighted = 0
        total_achieved = 0

        # Calculate totals from child table
        for item in self.table_qwvz:
            total_weighted += flt(item.weighted)
            total_achieved += flt(item.achieved)

        # Calculate percentages
        self.total_weighted_percent = total_weighted
        self.total_achieved_percent = total_achieved

        # Show success message
        frappe.msgprint("Totals calculated successfully: Weighted = {:.2f}%, Achieved = {:.2f}%".format(total_weighted, total_achieved))

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

