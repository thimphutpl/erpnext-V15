# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class NoteRemark(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		action: DF.Literal["", "Apply", "Forward", "Approve", "Reject", "Review"]
		content: DF.TextEditor | None
		designation: DF.Data | None
		employee: DF.Link | None
		employee_name: DF.Data | None
		forward_to: DF.Link | None
		name: DF.Int | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		print_hide: DF.Check
		remark: DF.TextEditor | None
		remark_date: DF.Date | None
		user: DF.Link
	# end: auto-generated types
	pass
