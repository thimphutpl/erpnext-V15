# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class CompactAgreement(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.compact_agreement.doctype.compact_agreement_items.compact_agreement_items import CompactAgreementItems
		from frappe.types import DF

		agency: DF.Link | None
		amended_from: DF.Link | None
		company: DF.Link | None
		fiscal_year: DF.Link | None
		table_vaeg: DF.Table[CompactAgreementItems]
	# end: auto-generated types
	# pass
      
@frappe.whitelist()
def make_compact_review(source_name, target_doc=None): 
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
				"validation": {"docstatus": ["=", 1], "compact_review": ["is", None]}
			},
		}, target_doc)
	return doc      


# from frappe.model.document import Document

# class CompactAgreement(Document):
#     # begin: auto-generated types
# 	# This code is auto-generated. Do not modify anything in this block.

# 	from typing import TYPE_CHECKING

# 	if TYPE_CHECKING:
# 		from erpnext.compact_agreement.doctype.compact_agreement_items.compact_agreement_items import CompactAgreementItems
# 		from frappe.types import DF

# 		agency: DF.Link | None
# 		amended_from: DF.Link | None
# 		company: DF.Link | None
# 		fiscal_year: DF.Link | None
# 		table_vaeg: DF.Table[CompactAgreementItems]
# 	# end: auto-generated types

# def before_print(self, settings=None):
#         """Use the first suppliers data to render the print preview."""
#         if self.vendor or not self.suppliers:
#             # If a specific supplier is already set, via Tools > Download PDF,
#             # we don't want to override it.
#             return

#         self.update_supplier_part_no(self.suppliers[0].supplier)

# def on_cancel(self):
#         self.db_set("status", "Cancelled")
        
# def group_items_by_output(self):
#         """Group items based on 'output' checkbox in child table."""
#         groups = []
#         current_group = []

#         for item in self.table_vaeg:
#             if item.output:
#                 # If we encounter an item with the output checkbox checked
#                 if current_group:
#                     # Add the previous group to groups list
#                     groups.append(current_group)
#                 # Start a new group
#                 current_group = [item]
#             else:
#                 # Continue adding to the current group
#                 current_group.append(item)

#         # Append the last group if it exists
#         if current_group:
#             groups.append(current_group)

#         return groups

# def get_group_for_item(self, item_to_delete):
#         """Find the group that contains the item to delete."""
#         grouped_items = self.group_items_by_output()

#         # Find and return the group that contains the item to delete
#         for group in grouped_items:
#             if item_to_delete in group:
#                 return group
#         return []

# def before_delete(self, item_to_delete):
#         """Delete the entire group when the checked output item is deleted."""
#         if item_to_delete.output:
#             # Find the group that contains the item and delete the whole group
#             group = self.get_group_for_item(item_to_delete)
#             for item in group:
#                 item.delete()
#         else:
#             # Just delete the individual item
#             item_to_delete.delete()

# def on_trash(self):
#         """Override the trash method to ensure group deletion works."""
#         for item in self.table_vaeg:
#             self.before_delete(item)				
   



	
