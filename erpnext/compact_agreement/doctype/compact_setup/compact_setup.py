# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint, flt, nowdate, money_in_words

class CompactSetup(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.compact_agreement.doctype.compact_agreement_items.compact_agreement_items import CompactAgreementItems
		from frappe.types import DF

		agency: DF.Link
		amended_from: DF.Link | None
		company: DF.Link
		fiscal_year: DF.Link
		table_vaeg: DF.Table[CompactAgreementItems]
	# end: auto-generated types

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.compact_agreement.doctype.compact_agreement_items.compact_agreement_items import CompactAgreementItems
		from frappe.types import DF

		agency: DF.Link | None
		amended_from: DF.Link | None
		company: DF.Link | None
		fiscal_year: DF.Link | None
		table_vaeg: DF.Table[CompactAgreementItems]

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.compact_setup.doctype.compact_setup_items.compact_setup_items import CompactSetupItems
		from frappe.types import DF

		agency: DF.Link | None
		amended_from: DF.Link | None
		company: DF.Link | None
		fiscal_year: DF.Link | None
		table_vaeg: DF.Table[CompactSetupItems]

# def before_save(self):
#         """Save data of Compact Setup within the Compact Setup doctype."""
#         self.last_updated = nowdate()
#         frappe.msgprint("Compact Setup data has been saved successfully.")
def before_save(self):
    frappe.msgprint(f"Current workflow state: {self.workflow_state}")
    if self.workflow_state == "Draft":  # Or the specific state you're interested in
        frappe.throw("Cannot save document in Draft state.")
    """Ensure total weighted does not exceed 100%."""
    total_weighted = 0

    # Calculate the total weighted from the child table
    for item in self.table_vaeg:
        total_weighted += flt(item.weighted)

    # Check if the total weighted exceeds 100
    if total_weighted > 100:
        frappe.throw("The total weighted percentage cannot exceed 100%. Current total: {:.2f}%".format(total_weighted))

    # If the total weighted is valid, proceed with saving the data
    self.last_updated = nowdate()
    frappe.msgprint("Compact Setup data has been saved successfully.")

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

def show_create_review_button(self):
        """Display the 'Create Review' button only for Head of OPM if approved."""
        return frappe.session.user == "PMS Compact Approver" and self.workflow_state == "Approved"

def show_create_evaluation_button(self):
        """Display the 'Create Evaluation' button only after review is completed."""
        return frappe.session.user == "PMS Compact Approver" and self.review_completed

@frappe.whitelist()
def make_compact_review(source_name, target_doc=None):
    # """Map fields from Compact Setup to Compact Review."""
    # if frappe.session.user != "Head of OPM":
    #     frappe.throw("Only the Head of OPM can create a Compact Review.")

    def update_date(obj, target, source_parent):
        target.posting_date = nowdate()

    doc = get_mapped_doc("Compact Setup", source_name, {
        "Compact Setup": {
            "doctype": "Compact Review",
            "field_map": {
                "name": "compact_review",
                "date": "compact_setup_date"
            },
            "postprocess": update_date,
        },
        "Compact Agreement Items": {
            "doctype": "Compact Agreement Items Review",
            "field_map": {
                "target": "target",
                "deliveries": "deliveries",
                "deadlines": "deadlines",
                "weighted": "weighted",
                "remarks": "remarks"
            }
        }
    }, target_doc)

    return doc

