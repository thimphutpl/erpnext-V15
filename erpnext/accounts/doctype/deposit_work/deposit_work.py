# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt


class DepositWork(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.deposit_work_expense.deposit_work_expense import DepositWorkExpense
		from erpnext.accounts.doctype.deposit_work_received.deposit_work_received import DepositWorkReceived
		from frappe.types import DF

		balance_amount: DF.Currency
		branch: DF.Link
		cost_center: DF.Link
		customer: DF.Link | None
		e_items: DF.Table[DepositWorkExpense]
		end_date: DF.Date | None
		name_of_work: DF.Data
		r_items: DF.Table[DepositWorkReceived]
		start_date: DF.Date | None
		total_expense_amount: DF.Currency
		total_received_amount: DF.Currency
		work_type: DF.Literal["", "Bridge Launching", "Bridge De-Launching", "Deposit Work"]
	# end: auto-generated types
	def validate(self):
		expense = received = 0
		for a in self.r_items:
			received += flt(a.amount)

		for d in self.e_items:
			expense += flt(d.amount)

		self.total_received_amount = received
		self.total_expense_amount = expense
		self.balance_amount = flt(received) - flt(expense)
