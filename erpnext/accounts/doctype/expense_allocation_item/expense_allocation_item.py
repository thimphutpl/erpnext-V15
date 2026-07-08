# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ExpenseAllocationItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		business_activity: DF.Link
		equipment: DF.Link | None
		equipment_number: DF.Data | None
		expense_for: DF.Literal["", "HSD", "Hire Charge", "Lubricant", "Operator Allowance", "OAP Salary", "Muster Roll Employee", "GCE", "Overtime Payment", "DFG Soelra", "GFG Soelra", "Thai Salary", "Indian Operators Salary", "Repair and Maintenance", "OJT", "Contract Employee", "Gas & Utility"]
		expense_type: DF.Data | None
		id_card: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		project: DF.Link
		quantity: DF.Data | None
		rate: DF.Currency
		remarks: DF.LongText | None
		time: DF.Float
	# end: auto-generated types
	pass
