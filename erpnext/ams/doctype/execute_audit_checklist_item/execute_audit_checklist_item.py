# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ExecuteAuditChecklistItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		audit_area_checklist: DF.Link
		audit_attachment: DF.Attach | None
		audit_remarks: DF.TextEditor | None
		auditee_attachment: DF.Attach | None
		auditee_remarks: DF.TextEditor | None
		nature_of_irregularity: DF.Link | None
		observation: DF.TextEditor | None
		observation_title: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		status: DF.Link
	# end: auto-generated types
	pass
