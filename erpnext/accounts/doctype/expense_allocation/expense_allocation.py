# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ExpenseAllocation(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.model.document import Document
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		cost_center: DF.Link | None
		cost_type: DF.Literal["HSD", "Hire Charge", "Lubricant", "Operator Allowance", "OAP Salary", "Muster Roll Employee", "GCE", "Overtime Payment", "DFG Soelra", "Thai Salary", "Indian Operators Salary", "Repair and Maintenance", "OJT", "Contract Employee"]
		items: DF.Table[Document]
		posting_date: DF.Date
		title: DF.Data
		total_amount: DF.Currency
	# end: auto-generated types
	
	def validate(self):
		if self.items:
			total = 0
			for d in self.items:
				total += flt(d.amount)
				self.total_amount= total
@frappe.whitelist()
def update_fetch_data(expense_for, expense_type):
	equipment_id = cid = ''
	if expense_for =="Equipment" and expense_type:
		equipment_id =frappe.db.get_value("Equipment",expense_type,"registration_number")

	elif expense_for=="Open Air Prisoner" and expense_type:
		cid =frappe.db.get_value("Open Air Prisoner",expense_type,"id_card")

	elif expense_for=="Operator" and expense_type:
		cid =frappe.db.get_value("Operator",expense_type,"id_card")

	elif expense_for=="Muster Roll Employee" and expense_type:
		cid =frappe.db.get_value("Muster Roll Employee",expense_type,"id_card")
	else:
		return
	return equipment_id, cid