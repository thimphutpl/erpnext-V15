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
		is_hsd_item: DF.Check
		issue_from: DF.Literal["Tanker", "Barrel"]
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
		self.update_posting_date_and_time()
		self.validate_branch()
		self.validate_data()
		# self.validate_posting_time()
		self.validate_uom_is_integer("stock_uom", "qty")
		""" ++++++++++ Ver 2.0.190509 Begins ++++++++++ """
		# Ver 2.0.190509, following method added by SHIV on 2019/05/21
		self.check_and_set_rate()
		self.set_tatal_amount()

	def validate_branch(self):
		if self.purpose == "Issue" and self.is_hsd_item and not self.tanker and self.issue_from !="Barrel":
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

	def on_submit(self):
		self.update_posting_date_and_time()
		if not self.items:
			frappe.throw("Should have a POL Issue Details to Submit")
		self.validate_data()
		self.check_and_set_rate()
		self.set_tatal_amount()
		self.make_gl_entries()
		""" ++++++++++ Ver 2.0.190509 Ends ++++++++++++ """
		
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
		self.delete_pol_entry()

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

		balance_qty = frappe.db.sql("""select qty, rate
			from `tabPOL Entry` 
			where branch='{branch}'
			and item ='{item}'
			{cond}
			order by timestamp(posting_date, posting_time) desc
			limit 1
			""".format(branch=self.branch, item=self.pol_type, cond =cond))
		if self.total_quantity and self.total_quantity > balance_qty[0][0]:
			frappe.throw("Total qty cannot be greater than tanker balance "+str(balance_qty[0][0]))
		else:
			self.tank_balance =balance_qty[0][0]
			self.rate = balance_qty[0][1]
	def make_gl_entries(self):
		gl_entries = []
		self.make_expense_gl_entry(gl_entries)
		self.make_advance_gl_entry(gl_entries)
		gl_entries = merge_similar_entries(gl_entries)
		make_gl_entries(gl_entries,update_outstanding="No",cancel=self.docstatus == 2)
	
	def make_expense_gl_entry(self, gl_entries):
		if flt(self.total_amount) > 0:
			if self.direct_consumption:
				expense_account = frappe.db.get_value("Equipment Category", self.equipment_category,'pol_advance_account')
				if not expense_account:
					frappe.throw("Please set POL Expense Account in Equipment Category "+str(self.equipment_category))
			else:
				expense_account = frappe.db.get_value("Company", self.company,'fuel_stock_account')
				if not expense_account:
					frappe.throw("Please set Fuel Stock Account in Company "+str(self.equipment_category))

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

	def make_advance_gl_entry(self, gl_entries):
		if flt(self.total_amount) > 0:
			advance_account = frappe.db.get_value("Company", self.company,'pol_advance_account')
			if not advance_account:
				frappe.throw("Please set POL Advance Account in  Company "+str(self.company))
			gl_entries.append(
				self.get_gl_dict({
					"account": advance_account,
					"credit": self.total_amount,
					"credit_in_account_currency": self.total_amount,
					"against_voucher": self.name,
					"party_type": "Supplier",
					"party": self.supplier,
					"against_voucher_type": self.doctype,
					"cost_center": self.cost_center,
					"voucher_type":self.doctype,
					"voucher_no":self.name
				}, self.currency))

	def set_tatal_amount(self):
		if self.rate and self.total_quantity:
			self.total_amount = self.rate * self.total_quantity
	

	def make_pol_entry(self):
		if getdate(self.posting_date) <= getdate("2024-03-31"):
			return
		if self.tanker:
			con = frappe.new_doc("POL Entry")
			con.flags.ignore_permissions = 1
			con.equipment = self.tanker
			con.pol_type = self.pol_type
			con.branch = self.branch
			con.posting_date = self.posting_date
			con.posting_time = self.posting_time
			con.qty = self.total_quantity
			con.reference_type = "POL Issue"
			con.reference_name = self.name
			con.type = "Issue"
			con.is_opening = 0
			con.submit()

		for a in self.items:
			if self.branch == a.equipment_branch:
				own = 1
			else:
				own = 0
			con = frappe.new_doc("POL Entry")
			con.flags.ignore_permissions = 1
			con.equipment = a.equipment
			con.pol_type = self.pol_type
			con.branch = a.equipment_branch
			con.posting_date = self.posting_date
			con.posting_time = self.posting_time
			con.qty = a.qty
			con.reference_type = "POL Issue"
			con.reference_name = self.name
			con.own_cost_center = own
			if self.purpose == "Issue":
				con.type = "Receive"
			else:
				con.type = "Stock"
			con.is_opening = 0
			con.submit()

	def delete_pol_entry(self):
		frappe.db.sql("delete from `tabPOL Entry` where reference_name = %s", self.name)
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
def get_tanker_data(doctype, txt, searchfield, start, page_len, filters):
	if not filters.get('branch'):
		frappe.throw(_("Branch is required to fetch the equipment."))
	
	tanker_data = frappe.db.sql("""
		SELECT
			e.name, e.equipment_type, e.registration_number
		FROM `tabEquipment` e
		WHERE e.branch = %(branch)s
		  AND e.is_disabled != 1
		  AND e.not_cdcl = 0
		  AND EXISTS (
			  SELECT 1
			  FROM `tabEquipment Type` t
			  WHERE t.name = e.equipment_type
				AND t.is_container = 1
		  )
		  AND ({key} LIKE %(txt)s
			   OR e.equipment_type LIKE %(txt)s
			   OR e.registration_number LIKE %(txt)s)
		{mcond}
		ORDER BY
			IF(LOCATE(%(_txt)s, e.name), LOCATE(%(_txt)s, e.name), 99999),
			IF(LOCATE(%(_txt)s, e.equipment_type), LOCATE(%(_txt)s, e.equipment_type), 99999),
			IF(LOCATE(%(_txt)s, e.registration_number), LOCATE(%(_txt)s, e.registration_number), 99999),
			idx DESC,
			e.name, e.equipment_type, e.registration_number
		LIMIT %(start)s, %(page_len)s
	""".format(
		key=searchfield,
		mcond=get_match_cond(doctype)
	), {
		"txt": f"%{txt}%",
		"_txt": txt.replace("%", ""),
		"start": start,
		"page_len": page_len,
		"branch": filters['branch']
	})

	return tanker_data

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


	
