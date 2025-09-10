# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class ConsolidationTransaction(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.consolidation_transaction_item.consolidation_transaction_item import ConsolidationTransactionItem
		from frappe.types import DF

		amended_from: DF.Link | None
		from_date: DF.Date | None
		items: DF.Table[ConsolidationTransactionItem]
		to_date: DF.Date | None
	# end: auto-generated types
	pass
@frappe.whitelist()
def make_adjustment_entry(source_name, target_doc=None):
        
        doclist = get_mapped_doc("Consolidation Transaction", source_name, {
                "Consolidation Transaction": {
						"doctype": "Consolidation Adjustment Entry",
						"field_map":{
								"name": "consolidation_transaction"
						},
                        }
        }, target_doc)
        return doclist