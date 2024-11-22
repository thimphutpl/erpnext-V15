# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AuditChecklist(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		audit_checklist: DF.Data
		audit_criteria: DF.Link
		is_disabled: DF.Check
		is_for_both: DF.Check
		is_for_ho: DF.Check
		type_of_audit: DF.Data
	# end: auto-generated types
	pass
