# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.custom_utils import check_future_date, get_branch_cc, prepare_gl, prepare_sl, check_budget_available
from frappe.utils import flt, cint, getdate
from erpnext.controllers.stock_controller import StockController
from erpnext.fleet_management.fleet_utils import get_pol_till, get_previous_km
from erpnext.accounts.general_ledger import (
	get_round_off_account_and_cost_center,
	make_gl_entries,
	make_reverse_gl_entries,
	merge_similar_entries,
)
from frappe.utils import nowdate, nowtime
from frappe.desk.reportview import get_match_cond
from erpnext.accounts.utils import get_fiscal_year
from erpnext.fleet_management.report.hsd_consumption_report.fleet_management_report import get_pol_tills, get_pol_consumed_tills

# from erpnext.fleet_management.report.fleet_management_report import get_pol_till
from erpnext.stock.utils import get_stock_balance
# from erpnext.fleet_management.fleet_utils import get_without_fuel_hire
from erpnext.fleet_management.maintenance_utils import get_without_fuel_hire
class POLIssue(StockController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.pol_issue_items.pol_issue_items import POLIssueItems
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		company: DF.Link
		cost_center: DF.Link | None
		currency: DF.Link | None
		fuel_book: DF.Link | None
		is_hsd_item: DF.Check
		issue_from: DF.Literal["Tanker", "Barrel", "Fuelbook"]
		item_name: DF.ReadOnly | None
		items: DF.Table[POLIssueItems]
		pol_type: DF.Link
		posting_date: DF.Date | None
		posting_time: DF.Time | None
		project: DF.Link | None
		purpose: DF.Literal["", "Issue", "Transfer"]
		rate: DF.Data | None
		registration_number: DF.ReadOnly | None
		remarks: DF.SmallText | None
		stock_uom: DF.ReadOnly | None
		tank_balance: DF.Float
		tanker: DF.Link | None
		total_amount: DF.Currency
		total_quantity: DF.Float
		transfer_amount: DF.Currency
		transfer_branch: DF.Link | None
		transfer_cost_center: DF.Link | None
		transfer_qty: DF.Float
		transfer_type: DF.Literal["", "Tanker to Tanker", "Barrel to Barrel", "Tanker to Barrel", "Barrel to Tanker"]
		warehouse: DF.Link | None
	# end: auto-generated types
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.pol_issue_items.pol_issue_items import POLIssueItems
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		company: DF.Link
		cost_center: DF.Link | None
		is_hsd_item: DF.Check
		issue_from: DF.Literal["Tanker", "Barrel"]
		item_name: DF.ReadOnly | None
		items: DF.Table[POLIssueItems]
		pol_type: DF.Link
		posting_date: DF.Date
		posting_time: DF.Time
		project: DF.Link | None
		purpose: DF.Literal["", "Issue", "Transfer"]
		rate: DF.Data | None
		registration_number: DF.ReadOnly | None
		remarks: DF.SmallText | None
		stock_uom: DF.ReadOnly | None
		tank_balance: DF.Float
		tanker: DF.Link | None
		total_amount: DF.Currency
		total_quantity: DF.Float
		warehouse: DF.Link | None

	def validate(self):
		self.validate_transfer_data()
		self.update_posting_date_and_time()
		self.validate_branch()
		self.validate_data()
		# self.validate_posting_time()
		self.validate_uom_is_integer("stock_uom", "qty")
		""" ++++++++++ Ver 2.0.190509 Begins ++++++++++ """
		# Ver 2.0.190509, following method added by SHIV on 2019/05/21
		self.check_and_set_rate()
		# self.set_tatal_amount()

	def validate_branch(self):
		if self.purpose == "Issue" and self.is_hsd_item and not self.tanker and self.issue_from not in ["Barrel","Fuelbook"]:
			frappe.throw("For HSD Issues, Tanker is Mandatory")

		if not self.is_hsd_item:
			self.tanker = ""

	def populate_data(self):
		cc = get_branch_cc(self.branch)
		self.cost_center = cc
		warehouse = frappe.db.get_value("Cost Center", cc, "warehouse")
		if not warehouse:
			frappe.throw(str(cc) + " is not linked to any Warehouse")
		self.warehouse = warehouse

	def validate_data(self):
		if not self.purpose:
			frappe.throw("Purpose is Missing")
		if not self.cost_center:
			frappe.throw("Cost Center are Mandatory")
		total_quantity = 0
		for a in self.items:
			if flt(a.qty) <= 0:
				frappe.throw("Quantity for <b>"+str(a.registration_number)+"</b> should be greater than 0")
			total_quantity = flt(total_quantity) + flt(a.qty)
		self.total_quantity = total_quantity
	def before_save(self):
		self.set_total_amount()
	def on_submit(self):
		self.update_posting_date_and_time()
		if self.purpose=="Issue" and not self.items:
			frappe.throw("Should have a POL Issue Details to Submit")
		self.validate_data()
		self.check_and_set_rate()
		self.make_gl_entries()
		self.make_pol_entry()

	def on_cancel(self):
		self.make_gl_entries_on_cancel()
		self.ignore_linked_doctypes = (
			"GL Entry",
			"Payment Ledger Entry",
			"Stock Ledger Entry",
			"Repost Item Valuation",
			"Serial and Batch Bundle",
		)	 
		self.make_pol_entry(cancel=True)

	def update_posting_date_and_time(self):
		self.posting_date = nowdate()
		self.posting_time =nowtime()

	def check_and_set_rate(self):
		if not self.pol_type:
			frappe.throw("POL Items is required")
		if self.issue_from =="Tanker":
			cond = "and equipment='{tanker}'".format(tanker=self.tanker)
		if self.issue_from =="Barrel":
			cond = "and is_barrel =1"
		elif self.issue_from =="Fuelbook":
			cond ="and is_fuel_book= 1"	
		b_qty = b_rate = 0
		balance_qty = frappe.db.sql("""select qty, rate
			from `tabPOL Entry` 
			where branch='{branch}'
			and item ='{item}'
			{cond}
			order by timestamp(posting_date, posting_time) desc
			limit 1
			""".format(branch=self.branch, item=self.pol_type, cond =cond),as_dict=True)
		if balance_qty:
			for x in balance_qty:
				b_qty = x.qty + b_qty
				b_rate =x.rate + b_rate
		if b_qty <= 0:
			frappe.throw("Tanker/Barrel has no fuel balance")
		if self.total_quantity and self.total_quantity > b_qty:
			frappe.throw("Total qty cannot be greater than tanker balance "+str(b_qty))
		else:
			self.tank_balance =b_qty
			self.rate = b_rate
	def set_total_amount(self):
		total_amount=0.0
		total_amount = flt(self.rate)*flt(self.total_quantity)
		self.total_amount = total_amount
	def make_gl_entries(self):
		gl_entries = []
		self.make_expense_gl_entry(gl_entries)
		self.make_advance_gl_entry(gl_entries)
		gl_entries = merge_similar_entries(gl_entries)
		make_gl_entries(gl_entries,update_outstanding="No",cancel=self.docstatus == 2)
	
	def make_expense_gl_entry(self, gl_entries):
		if self.purpose=="Issue":
			if flt(self.total_amount) > 0:
				expense_account = frappe.db.get_value("Company",self.company,"pol_expense_account")
				if not expense_account:
					frappe.throw("Please set POL Expense Account in Company")
				gl_entries.append(
					self.get_gl_dict({
						"account": expense_account,
						"debit": self.total_amount,
						"debit_in_account_currency": self.total_amount,
						"against_voucher": self.name,
						"against_voucher_type": self.doctype,
						"cost_center": self.cost_center,
						"voucher_type":self.doctype,
						"voucher_no":self.name
					}, self.currency))

		if self.purpose=="Transfer":
			if flt(self.transfer_amount) > 0:
				if self.transfer_type in ("Barrel to Barrel", "Tanker to Barrel"):
					dr_cost_center = self.transfer_cost_center
				elif self.transfer_type in ("Barrel to Tanker", "Tanker to Tanker"):
					for x in self.items:
						dr_cost_center = frappe.db.get_value("Branch",x.equipment_branch,"cost_center")
				else:
					dr_cost_center =""
				if not dr_cost_center or dr_cost_center=="":
					frappe.throw("Transfer Cost center is required")
				expense_account = frappe.db.get_value("Company",self.company,"fuel_stock_account")
				if not expense_account:
					frappe.throw("Please set Fuel Stock Account in Company")
				gl_entries.append(
					self.get_gl_dict({
						"account": expense_account,
						"debit": self.transfer_amount,
						"debit_in_account_currency": self.transfer_amount,
						"against_voucher": self.name,
						"against_voucher_type": self.doctype,
						"cost_center": dr_cost_center,
						"voucher_type":self.doctype,
						"voucher_no":self.name
					}, self.currency))

	def make_advance_gl_entry(self, gl_entries):
		credit_amount =0
		if self.purpose=="Transfer":
			credit_amount = self.transfer_amount
		if self.purpose=="Issue":
			credit_amount = self.total_amount
		if flt(credit_amount) > 0:
			advance_account = frappe.db.get_value("Company",self.company,"pol_advance_account")
			if not advance_account:
				frappe.throw("Please set Fuel Stock Account in  Company "+str(self.company))
			gl_entries.append(
				self.get_gl_dict({
					"account": advance_account,
					"credit": credit_amount,
					"credit_in_account_currency": credit_amount,
					"against_voucher": self.name,
					"against_voucher_type": self.doctype,
					"cost_center": self.cost_center,
					"voucher_type":self.doctype,
					"voucher_no":self.name
				}, self.currency))


	def make_pol_entry(self, cancel=False):
		if self.issue_from =="Barrel":
			book_type ="Barrel"
			cond ="and is_barrel = 1"
		elif self.issue_from =="Fuelbook":
			book_type="General Pol"
			cond ="AND is_fuel_book = 1 AND fuelbook='{fuelbook}'".format(fuelbook=self.fuel_book)
		
		else:
			book_type ="Common"
			cond ="and equipment='{tanker}'".format(tanker=self.tanker)
		balance_qty = frappe.db.sql("""select qty, rate, amount
			from `tabPOL Entry` 
			where branch='{branch}'
			and item ='{item}'
			{cond}
			order by timestamp(posting_date, posting_time) desc
			limit 1
			""".format(branch=self.branch, item=self.pol_type, cond=cond), as_dict=True)
		
		b_qty = total_amount = issue_qty = 0
		for raw in balance_qty:
			if not cancel:
				if raw.qty != self.tank_balance:
					frappe.throw("POL Received or Issue has been made after this transaction please make few changes and save this doc")
				if self.purpose=="Issue":
					b_qty = flt(raw.qty) - flt(self.total_quantity)
					issue_qty=flt(raw.qty)
					total_amount = raw.amount - self.total_amount
				if self.purpose=="Transfer":
					b_qty = flt(raw.qty) - flt(self.transfer_qty)
					issue_qty=flt(raw.qty)
					total_amount = raw.amount - self.transfer_amount
				# b_rate = flt(total_amount) / flt(b_qty)
			else:
				if self.purpose=="Issue":
					b_qty = flt(raw.qty) + flt(self.total_quantity)
					total_amount = flt(raw.amount) + flt(self.total_amount)
				if self.purpose=="Transfer":
					b_qty = flt(raw.qty) + flt(self.transfer_qty)
					total_amount = flt(raw.amount) + flt(self.transfer_amount)
				
				# b_rate = flt(total_amount) / flt(b_qty)

			# if flt(b_qty) <= 0:
			# 	b_qty = 0
			# 	total_amount = 0
			# else:
				total_amount = flt(issue_qty) * flt(self.rate)	



		con = frappe.new_doc("POL Entry")
		con.flags.ignore_permissions = 1
		if self.issue_from == "Barrel":
			con.is_barrel = 1
		elif self.issue_from == "Fuelbook":
			con.is_fuel_book = 1
		else:
			con.equipment = self.tanker
		con.book_type = book_type
		con.item = self.pol_type
		con.branch = self.branch
		con.fuelbook = self.fuel_book
		con.posting_date = nowdate()
		con.posting_time = nowtime()
		con.qty = b_qty
		con.issue_qty = issue_qty
		con.rate = self.rate
		con.amount = total_amount
		con.reference_type = "POL Issue"
		con.reference_name = self.name
		con.is_opening = 0
		con.submit()
		
		if self.purpose =="Transfer":
			branch=""
			if self.transfer_type in("Barrel to Barrel", "Tanker to Barrel"):
				branch= self.transfer_branch
				book_type ="Barrel"
				cond ="and is_barrel = 1"
			if self.transfer_type in ("Tanker to Tanker", "Barrel to Tanker"):
				count=0
				for x in self.items:
					branch=x.equipment_branch
					count=count+1
					equipment = x.equipment
					tr_qty=x.qty
				if count >=2:
					frappe.throw("Transfer can only be made to one equipment at a time")
				if not equipment or not tr_qty:
					frappe.throw("Receiver equipment and Qty is Required")
				book_type ="Common"
				cond ="and equipment='{equipment}'".format(equipment=equipment)
			if not branch or branch=="":
				frappe.throw("Transfer Branch or Equioment Branch is required")

			balance_qty = frappe.db.sql("""select qty, rate, amount
				from `tabPOL Entry` 
				where branch='{branch}'
				and item ='{item}'
				{cond}
				order by timestamp(posting_date, posting_time) desc
				limit 1
				""".format(branch=branch, item=self.pol_type, cond=cond), as_dict=True)
			
			b_qty = b_rate = total_amount = 0
			if balance_qty:
				for raw in balance_qty:
					if not cancel:
						b_qty = flt(raw.qty) + flt(self.transfer_qty)
						total_amount = flt(raw.amount) + flt(self.transfer_amount)
						b_rate = flt(total_amount) / flt(b_qty)
					else:
						b_qty = flt(raw.qty) - flt(self.transfer_qty)
						total_amount = flt(raw.amount) - flt(self.transfer_amount)
						if total_amount!=0 and b_qty!=0:
							b_rate = flt(total_amount) / flt(b_qty)
			else:
				b_qty = self.transfer_qty
				b_rate = self.rate
				total_amount = self.transfer_amount

			con = frappe.new_doc("POL Entry")
			con.flags.ignore_permissions = 1
			if self.transfer_type in ("Tanker to Tanker", "Barrel to Tanker"):	
				con.equipment = equipment
			if self.transfer_type in ("Tanker to Barrel", "Barrel to Barrel"):	
				con.is_barrel = 1
			con.book_type = book_type
			con.item = self.pol_type
			con.branch = branch
			con.posting_date = nowdate()
			con.posting_time = nowtime()
			con.qty = b_qty
			con.rate = b_rate
			con.amount = total_amount
			con.type="Issue"
			con.reference_type = "POL Issue"
			con.reference_name = self.name
			con.is_opening = 0
			con.submit()

	def validate_transfer_data(self):
		if self.purpose=="Transfer":
			if self.transfer_type in ("Barrel to Barrel","Tanker to Barrel"):
				if not self.transfer_branch:
					frappe.throw("Transfer branch is required when transfer type is "+str(self.transfer_type))
				if self.transfer_type=="Tanker to Barrel" and self.issue_from=="Barrel":
					frappe.throw("Issue from cannot be Barrel when  transfer type is "+str(self.transfer_type))
				if self.transfer_type=="Barrel to Barrel" and self.issue_from !="Barrel":
					frappe.throw("Issue from has to be Barrel when transfer type is "+str(self.transfer_type))
			if self.transfer_type not in ("Barrel to Barrel","Tanker to Barrel"):
				if self.transfer_type=="Barrel to Tanker" and self.issue_from!="Barrel":
					frappe.throw("Issue from has to be Barrel when  transfer type is "+str(self.transfer_type))
			if	self.transfer_type in ("Barrel to Tanker","Tanker to Tanker"):
				if not self.items:
					frappe.throw("Receiver Equipment is required when transfer type is "+str(self.transfer_type))
				if self.issue_from=="Barrel" and self.transfer_type=="Tanker to Tanker":
					frappe.throw("Issue from cannot be Barrel when transfer type is "+str(self.transfer_type))
				item_count =0
				for x in self.items:
					item_count = item_count+1	
					self.transfer_qty = x.qty
				if item_count >=2:
					frappe.throw("Transfer can only be made to one equipment at a time")

			if self.transfer_type in ("Barrel to Barrel","Tanker to Barrel") and self.items:
				frappe.throw("Receiver Equipment is not required when transfer type is "+str(self.transfer_type)+ "remove items details")
			self.transfer_amount = self.transfer_qty * self.rate
	# def set_tatal_amount(self):
	# 	if self.rate and self.total_quantity:
	# 		self.total_amount = self.rate * self.total_quantity
	# 	self.transfer_amount = self.transfer_qty * self.rate
	# 	if self.transfer_qty > self.tank_balance:
	# 		frappe.throw("Transfer balance cannot be greater than tanker/barrel balance")
	
# Equipment Balance
@frappe.whitelist()
def get_equipment_data(tanker, branch, pol_type):
	b_qty = b_rate = 0
	if not pol_type:
		frappe.throw("POL Items is required")
	
	balance_qty = frappe.db.sql("""select qty, rate
		from `tabPOL Entry` 
		where branch='{branch}'
		and item ='{item}'
		and equipment='{tanker}'
		order by timestamp(posting_date, posting_time) desc
		limit 1
		""".format(branch=branch, item=pol_type, tanker=tanker),as_dict=True)
	if balance_qty:
		for x in balance_qty:
			b_qty = b_qty+ x.qty
			b_rate = b_rate + x.rate

	if  b_qty > 0:
		return b_qty, b_rate
	else:
		frappe.throw("Tanker Balance is Zero for this Tanker")

@frappe.whitelist()
def get_tanker_details(tanker, posting_date, pol_type):
	received_till = get_pol_till("Stock", tanker, posting_date, pol_type)
	issue_till = get_pol_till("Issue", tanker, posting_date, pol_type)
	balance = flt(received_till) - flt(issue_till)
	return {"balance": balance}

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles: 
		return

	return """(
		`tabPOL Issue`.owner = '{user}'
		or
		exists(select 1
			from `tabEmployee` as e
			where e.branch = `tabPOL Issue`.branch
			and e.user_id = '{user}')
		or
		exists(select 1
			from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
			where e.user_id = '{user}'
			and ab.employee = e.name
			and bi.parent = ab.name
			and bi.branch = `tabPOL Issue`.branch)
	)""".format(user=user)


	
