# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DirectAccountabilityItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.ams.doctype.accountable_employee.accountable_employee import AccountableEmployee
		from frappe.types import DF

		checklist: DF.Link | None
		child_ref: DF.Data | None
		employee: DF.TableMultiSelect[AccountableEmployee]
		observation: DF.TextEditor | None
		observation_title: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		supervisor: DF.Link | None
		supervisor_name: DF.Data | None
	# end: auto-generated types
	pass
