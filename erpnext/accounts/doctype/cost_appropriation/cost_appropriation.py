# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from erpnext.accounts.general_ledger import make_gl_entries
from frappe import _
from erpnext.controllers.accounts_controller import AccountsController


class CostAppropriation(AccountsController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.model.document import Document
		from frappe.types import DF

		account: DF.Link | None
		amended_from: DF.Link | None
		applied_by: DF.Link | None
		approved_by: DF.Link | None
		branch: DF.Link
		company: DF.Link
		cost_center: DF.Link | None
		cost_type: DF.Literal["HSD", "Hire Charge", "Lubricant", "Operator Allowance", "OAP Salary", "Muster Roll Employee", "GCE", "Overtime Payment", "DFG Soelra", "Thai Salary", "Indian Operators Salary", "Repair and Maintenance", "OJT", "Contract Employee"]
		from_date: DF.Date
		items: DF.Table[Document]
		posting_date: DF.Date
		remarks: DF.LongText | None
		title: DF.Data | None
		to_date: DF.Date
		total_amount: DF.Currency
		verified_by: DF.Link | None
	# end: auto-generated types

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.model.document import Document
		from frappe.types import DF

		amended_from: DF.Link | None
		applied_by: DF.Link | None
		approved_by: DF.Link | None
		branch: DF.Link
		cost_center: DF.Link | None
		cost_type: DF.Literal["HSD", "Hire Charge", "Lubricant", "Operator Allowance", "OAP Salary", "Muster Roll Employee", "GCE", "Overtime Payment", "DFG Soelra", "Thai Salary", "Indian Operators Salary", "Repair and Maintenance", "OJT", "Contract Employee"]
		from_date: DF.Date
		items: DF.Table[Document]
		posting_date: DF.Date
		remarks: DF.LongText | None
		title: DF.Data | None
		to_date: DF.Date
		total_amount: DF.Currency
		verified_by: DF.Link | None
	# end: auto-generated types
	def validate(self):
		self.validate__accounts()
		if self.items:
			total = 0
			for d in self.items:
				total += flt(d.amount)
				self.total_amount= total
		# self.set_user(self)

	def validate__accounts(self):
		if self.cost_type == 'Hire Charge':
			self.account = frappe.db.get_value ("Company",self.company,"hire_charge")
		if self.cost_type == 'OJT':
			self.account = frappe.db.get_value ("Company",self.company,"ojt")
		if self.cost_type == 'Contract Employee':
			self.account = frappe.db.get_value ("Company",self.company,"contract_employee")
		if self.cost_type == 'DFG Soelra':
			self.account = frappe.db.get_value ("Company",self.company,"dfg_soelra")
		if self.cost_type == 'Thai Salary':
			self.account = frappe.db.get_value ("Company",self.company,"thai_salary")
		if self.cost_type == 'Indian Operators Salary':
			self.account = frappe.db.get_value ("Company",self.company,"indian_operators_salary")
		if self.cost_type == 'Repair and Maintenance':
			self.account = frappe.db.get_value ("Company",self.company,"repair_and_maintenance")
		if self.cost_type == 'HSD':
			self.hsd = frappe.db.get_value ("Company",self.company,"hsd")
		
		if self.cost_type == 'Lubricant':
			self.account = frappe.db.get_value ("Company",self.company,"lubricant")
		if self.cost_type == 'GCE':
			self.account = frappe.db.get_value ("Company",self.company,"gce")
		if self.cost_type == 'Overtime Payment':
			self.hsd = frappe.db.get_value ("Company",self.company,"overtime_payment")
		
		if self.cost_type == 'Muster Roll Employee':
			self.account = frappe.db.get_value ("Company",self.company,"muster_roll_employee")
			if self.cost_type =='Operator Allowance':
				self.account = frappe.db.get_value ("Company",self.company,"operator_allowance")
		if self.cost_type == 'OAP Salary':
			self.account = frappe.db.get_value ("Company",self.company,"oap_salary")
				

	def on_submit(self):
		self.post_gl_entry()

	def on_cancel(self):
		self.post_gl_entry()
	@frappe.whitelist()
	def get_details(self):
		query = """ select 
					ea.posting_date, 
					eai.project, 
					eai.equipment_number, 
					eai.amount,
					eai.business_activity,
					ea.name as reference_no 
			from `tabExpense Allocation` ea,
			`tabExpense Allocation Item` eai  
			where ea.name = eai.parent  
			and ea.posting_date >= '{0}' 
			and ea.posting_date <= '{1}' 
			and ea.docstatus = 1 
			and ea.branch = '{2}' 
			and ea.cost_type = '{3}'
			and not exists (
				select 1 from `tabCost Appropriation Item` i
				inner join `tabCost Appropriation` a
				on i.parent = a.name
				where i.reference_no = ea.name
				and a.docstatus = 1
			)""".format(self.from_date, self.to_date, self.branch, self.cost_type)	
		
		entries = frappe.db.sql(query, as_dict=True)
		if not entries:
			frappe.msgprint("No Record Found")

		self.set('items', [])
		for d in entries:
			row = self.append('items', {})
			row.update(d)
	
	def post_gl_entry(self):
		gl_entries   = []
		if self.total_amount > 0:
			data = frappe.db.sql("""select round(sum(amount),2) as amount, project from `tabCost Appropriation Item` where parent = '{}' group by project""".format(self.name), as_dict = 1)
			# frappe.throw(str(data))
			for a in data:
				gl_entries.append(
					self.get_gl_dict({
						"account": self.account,
						"debit": round(flt(a.amount) ,2),
						"debit_in_account_currency": round(flt(a.amount) ,2),
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
					"account": self.account,
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

