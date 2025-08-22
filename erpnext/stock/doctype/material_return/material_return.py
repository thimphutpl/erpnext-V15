# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock.utils import get_stock_balance
from frappe.utils import cstr, flt, cint, get_datetime
from erpnext.custom_utils import check_future_date, get_branch_cc, prepare_gl, prepare_sl
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.stock_controller import StockController


class MaterialReturn(StockController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.stock.doctype.material_return_item.material_return_item import MaterialReturnItem
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		company: DF.Link
		cost_center: DF.Link
		items: DF.Table[MaterialReturnItem]
		old_mr_id: DF.Data
		posting_date: DF.Date
		posting_time: DF.Time
		remarks: DF.SmallText | None
		title: DF.Data
	# end: auto-generated types
	
	def validate(self):
		check_future_date(self.posting_date)
		self.validate_details()
	

	def validate_details(self):
		if not self.old_mr_id:
			frappe.throw("OLD MR ID is required")
		for a in self.items:
			expense_account = frappe.db.get_value("Item Default",{"parent":a.item_code}, "expense_account")
			a.amount = flt(a.qty) * flt(a.basic_rate)
			a.cost_center = self.cost_center
			a.expense_account = expense_account

	def on_submit(self):
		self.make_sl_entry()
		self.make_gl_entry()

	def on_cancel(self):
		self.make_sl_entry()
		self.make_gl_entry()

	def make_sl_entry(self):
		sl_entries = []
		for d in self.get('items'):
			if cstr(d.warehouse):
				sl_entries.append(self.get_sl_entries(d, {
					"warehouse": cstr(d.warehouse),
					"actual_qty": flt(d.qty),
					"incoming_rate": flt(d.valuation_rate, 2)
				}))

		if self.docstatus == 2:
				sl_entries.reverse()

		self.make_sl_entries(sl_entries, self.amended_from and 'Yes' or 'No')
	
	def make_gl_entry(self):
		gl_entries = []

		for a in self.items:
			inter_company_account = frappe.db.get_value("Company", self.company, "inter_company_account")
			if not a.expense_account:
				frappe.throw("Expense Account is mandatory for Item {}".format(a.item_name))
			wh_account = frappe.db.get_value("Warehouse", a.warehouse, "account")
			if not wh_account:
				frappe.throw(str(self.warehouse) + " Please set Account for warehouse.")

			expense_account = a.expense_account
			if not expense_account:
				frappe.throw("Expense Account in Item for {}".format(a.item_name))
			expense_project =""
			if a.project:
				expense_project = a.project
			
			gl_entries.append(
				prepare_gl(self, {"account": expense_account,
						"credit": flt(a.amount),
						"credit_in_account_currency": flt(a.amount),
						"cost_center": a.project_cost_center,
						"remarks": a.remarks,
						"project": expense_project
						})
				)
			gl_entries.append(
			prepare_gl(self, {"account": inter_company_account,
					"debit": flt(a.amount),
					"debit_in_account_currency": flt(a.amount),
					"cost_center": a.project_cost_center,
					"remarks": a.remarks,
					"project": expense_project
				})
			)
			gl_entries.append(
				prepare_gl(self, {"account": wh_account,
						"debit": flt(a.amount),
						"debit_in_account_currency": flt(a.amount),
						"cost_center": self.cost_center,
						"remarks": a.remarks
					})
				)
			gl_entries.append(
				prepare_gl(self, {"account": inter_company_account,
						"credit": flt(a.amount),
						"credit_in_account_currency": flt(a.amount),
						"cost_center": self.cost_center,
						"remarks": a.remarks
						})
				)

		if gl_entries:
			make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=False)

