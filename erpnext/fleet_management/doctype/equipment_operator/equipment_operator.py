# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class EquipmentOperator(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		contact_number: DF.Data | None
		employee_type: DF.Literal["", "Employee", "Muster Roll Employee"]
		end_date: DF.Date | None
		license_no: DF.Data | None
		operator: DF.Link
		operator_name: DF.ReadOnly | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		start_date: DF.Date
	# end: auto-generated types
	pass
