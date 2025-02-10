# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt, cint, nowdate, getdate, formatdate, money_in_words
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.custom_utils import check_future_date, get_branch_cc, prepare_gl, prepare_sli
from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.controllers.stock_controller import StockController

class ImprestRecoup(StockController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.imprest_advance_item.imprest_advance_item import ImprestAdvanceItem
		from erpnext.accounts.doctype.imprest_recoup_item.imprest_recoup_item import ImprestRecoupItem
		from frappe.types import DF

		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Link | None
		approver_name: DF.Data | None
		balance_amount: DF.Currency
		branch: DF.Link
		cheque_date: DF.Date | None
		cheque_no: DF.Data | None
		clearance_date: DF.Date | None
		company: DF.Link
		cost_center: DF.Link
		dispatch: DF.Data | None
		final_je: DF.Data | None
		final_settlement: DF.Literal["", "Yes", "No"]
		imprest_advance_list: DF.Table[ImprestAdvanceItem]
		imprest_type: DF.Link
		items: DF.Table[ImprestRecoupItem]
		journal_entry: DF.Data | None
		opening_balance: DF.Currency
		party: DF.DynamicLink | None
		party_type: DF.Literal["", "Employee"]
		pay_torecd_from: DF.Data | None
		posting_date: DF.Date
		project: DF.Link | None
		remarks: DF.SmallText
		title: DF.Data
		total_amount: DF.Currency
	# end: auto-generated types

	def validate(self):
		# validate_workflow_states(self)
		self.calculate_amount()
		self.set_required_data()
		self.set_recoup_account(validate=True)
		# if self.workflow_state != "Recouped":
		# 	notify_workflow_states(self)
	
	def set_recoup_account(self, validate=False):
		for d in self.items:
			if not d.account or not validate:
				d.account = get_imprest_recoup_account(d.recoup_type, self.company)[
					"account"
				]

	def calculate_amount(self):
		total_payable_amt = sum(d.amount for d in self.items) if self.items else 0
		self.total_amount = total_payable_amt

	def on_submit(self):
		self.make_gl_entry()
		self.update_stock_ledger()

		
	def on_cancel(self):
		self.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry")
		self.make_gl_entry()
		self.update_stock_ledger()
		# notify_workflow_states(self)


	def set_required_data(self):
		if not self.branch or not self.imprest_type:
			frappe.msgprint("Set Branch or Imprest")
		opening_balance = frappe.db.get_value("Branch Imprest Item",{"parent":self.branch,"imprest_type":self.imprest_type},"imprest_limit")
		imprest_amount = closing_amount =0
		if not opening_balance:
			frappe.throw("Set Imprest limit for branch " +self.branch+ "Imprest type "+self.imprest_type)
		for row in self.get('items'):
			imprest_amount = imprest_amount + row.amount
		
		self.opening_balance= opening_balance
		self.total_amount =imprest_amount
		self.balance_amount =flt(opening_balance) -  flt(imprest_amount)
		if imprest_amount > opening_balance:
			frappe.throw("Purchase Amount cannot be more than Imprest Limit")

	def make_gl_entry(self):
		gl_entries = []
		bank_account = frappe.db.get_value("Branch",self.branch,"expense_bank_account")
		if not bank_account:
			frappe.throw(_("Expense Bank Account is not defined in Branch '{0}'.").format(self.branch))
	
		wh = frappe.get_doc("Cost Center", self.cost_center).warehouse
		wh_account = frappe.db.get_value("Warehouse",wh, "account")
	
		if not wh_account:
			frappe.throw("Please Set Account In Warehouse '{}'".format(wh))
		gl_entries   = []
		if self.total_amount > 0:
			for a in self.get("items"):
				gl_entries.append(
					self.get_gl_dict({
						"account": a.account,
						"debit": round(flt(a.amount) ,2),
						"debit_in_account_currency":round(flt(a.amount) ,2),
						"voucher_no": self.name,
						"voucher_type": self.doctype,
						"project":a.project,
						"cost_center":self.cost_center,
						"business_activity": a.business_activity,
						"against_voucher_type":	self.doctype,
						"against_voucher": self.name,
					}
				))
			gl_entries.append(
				self.get_gl_dict({
					"account": bank_account,
					"debit": ,
					"credit": self.total_amount,
					"credit_in_account_currency": self.total_amount,
					"voucher_no": self.name,
					"voucher_type": self.doctype,
					"cost_center": self.cost_center,
					"business_activity": a.business_activity,
					"against_voucher_type":	self.doctype,
					"against_voucher": self.name,
				}
			))
			make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)
		else:
			frappe.throw("Total Amount is Zero")

	def update_stock_ledger(self):
		sl_entries = []
		wh = frappe.get_value("Cost Center", self.cost_center,"warehouse")
		for a in self.get("items"):
			if a.item_code and a.maintain_stock and (frappe.db.exists("Item", {"name": a.item_code, "is_stock_item": 1})):
				# frappe.throw("TTTT")
				sl_entries.append(
					prepare_sli(self, {
						"item_code": a.item_code,
						"posting_date":self.posting_date,
						"qty": flt(a.quantity),
						"warehouse": wh,
						"stock_uom": a.uom,
						"voucher_type":self.doctype,
						"voucher_no": self.name,
						"incoming_rate": round(flt(a.rate), 2),
						"company":self.company
					}))
			if self.docstatus == 2:
				sl_entries.reverse()
				self.make_sl_entries(sl_entries, 'Yes' if self.amended_from else 'No')
			else:
				self.make_sl_entries(sl_entries, 'Yes' if self.amended_from else 'No')
	

@frappe.whitelist()
def get_imprest_recoup_account(recoup_type, company):
	account = frappe.db.get_value(
		"Imprest Recoup Account", {"parent": recoup_type, "company": company}, "default_account"
	)
	if not account:
		frappe.throw(
			_("Set the default account for the {0} {1}").format(
				frappe.bold("Recoup Type"), get_link_to_form("Recoup Type", recoup_type)
			)
		)
	return {"account": account}

@frappe.whitelist()
def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	# if user == "Administrator" or "System Manager" in user_roles or "Accounts User" in user_roles or "Account Manager" in user_roles: 
	if any(role in user_roles for role in {"Administrator", "System Manager", "Accounts User", "Account Manager"}):
		return

	return """(
		owner = '{user}'
		or
		(approver = '{user}' and workflow_state not in  ('Draft','Rejected','Cancelled'))
	)""".format(user=user)