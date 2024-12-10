# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DocumentApprover(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.stock.doctype.approver_item.approver_item import ApproverItem
		from frappe.types import DF

		table_1: DF.Table[ApproverItem]
	# end: auto-generated types
	pass
