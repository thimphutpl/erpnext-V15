# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, qb, throw
from frappe.utils import flt, cint, cstr, fmt_money, formatdate, nowtime, getdate
from erpnext.custom_utils import check_future_date
from erpnext.controllers.stock_controller import StockController
from erpnext.accounts.general_ledger import (
	get_round_off_account_and_cost_center,
	make_gl_entries,
	make_reverse_gl_entries,
	merge_similar_entries,
)
from erpnext.accounts.party import get_party_account

from erpnext.accounts.utils import get_fiscal_year
from erpnext.custom_utils import check_future_date, get_branch_cc, prepare_gl, prepare_sl, check_budget_available

class POLReceive(StockController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.pol_receive_advance.pol_receive_advance import POLReceiveAdvance
		from erpnext.fleet_management.doctype.pol_receive_item.pol_receive_item import POLReceiveItem
		from frappe.types import DF

		advances: DF.Table[POLReceiveAdvance]
		amended_from: DF.Link | None
		apply_gst: DF.Check
		branch: DF.Link
		company: DF.Link
		cost_center: DF.Link | None
		current_km: DF.Float
		equipment: DF.Link
		equipment_category: DF.Link | None
		equipment_name: DF.Data | None
		for_machineries: DF.Check
		fuel_type: DF.Link
		fuelbook: DF.Link
		gst_account: DF.Link | None
		gst_amount: DF.Currency
		item_name: DF.Data | None
		items: DF.Table[POLReceiveItem]
		jv: DF.Link | None
		km_difference: DF.Float
		mileage: DF.Float
		od_amount: DF.Currency
		posting_date: DF.Date
		posting_time: DF.Time | None
		previous_km: DF.Float
		remarks: DF.SmallText | None
		supplier: DF.Link
		total_allocated_amount: DF.Currency
		total_amount: DF.Currency
		total_amount_before_gst: DF.Currency
		total_qty: DF.Float
		uom: DF.Link | None
	# end: auto-generated types


	def validate(self):
		check_future_date(self.posting_date)
		self.validate_advance()
		self.set_allocated_amount()
		self.validate_equipment_and_branch()

	def on_submit(self):
		self.update_pol_advance()
		# self.make_gl_entries()
		
		gl_entries = self.get_gl_entries()
		make_gl_entries(gl_entries)
		self.make_pol_entry()
		# if not self.is_opening:
		#   self.post_journal_entry()
		#   self.update_pol_advance()
		# else:
		#   self.status = "Paid"
		
	#Cancel
	def on_cancel(self):
		from erpnext.accounts.utils import unlink_ref_doc_from_payment_entries

		unlink_ref_doc_from_payment_entries(self)
		self.ignore_linked_doctypes = ("GL Entry", "Stock Ledger Entry", "Payment Ledger Entry", "POL Entry")
		self.update_pol_advance(cancel=True)
		gl_entries = self.get_gl_entries()
		make_gl_entries(gl_entries, cancel=True)
		self.cancel_pol_entry()


		# self.ignore_linked_doctypes = (
		# 	"GL Entry",
		# 	"Payment Ledger Entry",
		# )


	# def before_save(self):
	# 	if not self.advances:
	# 		frappe.throw("Advanced for POL is needed for the equipment", self.equipment)   


	def update_pol_advance(self, cancel=False):
		for adv in self.advances:
			allocated_amount = 0.0
			if flt(adv.allocated_amount) > 0:
				if flt(adv.balance_amount) < flt(adv.allocated_amount) and self.docstatus < 2:
					frappe.throw(_("Advance#{0} : Allocated amount Nu. {1}/- cannot be more than Advance Balance Nu. {2}/-").format(adv.reference_name, "{:,.2f}".format(flt(adv.allocated_amount)),"{:,.2f}".format(flt(adv.balance_amount))))
				else:
					allocated_amount = -1 * flt(adv.allocated_amount) if cancel else flt(adv.allocated_amount)


					adv_doc = frappe.get_doc("POL Advance", adv.reference_name)
					adv_doc.adjusted_amount = flt(adv_doc.adjusted_amount) + flt(allocated_amount)
					adv_doc.balance_amount    = flt(adv_doc.balance_amount) - flt(allocated_amount)
					adv_doc.save(ignore_permissions = True)
		
		if flt(self.od_amount):
			for d in self.get('advances'):
				od = -1 * flt(self.od_amount) if cancel else flt(self.od_amount)
				doc = frappe.get_doc("POL Advance", d.reference_name)
				doc.od_amount = flt(doc.od_amount) + flt(od)
				doc.od_balance = flt(doc.od_balance) + flt(od)
				doc.save(ignore_permissions = True)

	def validate_equipment_and_branch(self):
		equipment_doc = frappe.get_doc("Equipment", self.equipment)
		if self.branch != equipment_doc.branch:
			frappe.throw("Equipment's branch and Branch do not match")   

	def validate_advance(self):
		if not self.get('advances'):
			frappe.throw("POL Advance not found for select branch and equipment")
		
		valid_advances = [
			d for d in self.advances
			if flt(d.balance_amount) > 0
		]

		if not valid_advances:
			frappe.throw("Balance amount must be greater than zero")

	def set_allocated_amount(self):
		total_allocated = 0.0
		if flt(self.total_amount):
			allocated_amount = flt(self.total_amount)
			balance = 0.0
			for d in self.get("advances"):
				balance += flt(d.balance_amount)
				if d.balance_amount >= allocated_amount:
					d.allocated_amount = allocated_amount
					total_allocated += flt(d.allocated_amount)
					allocated_amount = 0
				elif d.balance_amount < allocated_amount:
					d.allocated_amount = d.balance_amount
					total_allocated += flt(d.allocated_amount)
					allocated_amount = flt(allocated_amount) - flt(d.balance_amount)
			# frappe.throw(balance)
			if flt(self.total_amount, 2) > balance:
				frappe.throw("Total amount is more than balance amount")
		self.total_allocated_amount = flt(total_allocated)
		if flt(self.total_amount, 2) > flt(self.total_allocated_amount):
			self.od_amount = flt(self.total_amount) - flt(self.total_allocated_amount)


	# Ver 2.0.190509, Following method created by SHIV on 2019/05/24
	def get_gl_entries(self, warehouse_account=None):
		gl_entries = []


		# creditor_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_pol_advance_account")
		creditor_account = frappe.db.get_value("Company", self.company, "pol_advance_account")
		if not creditor_account:
			frappe.throw("Set Default Payable Account in Company")


		# expense_account = self.get_expense_account()
		expense_account = frappe.db.get_value("Equipment Category", self.equipment_category, "pol_advance_account")
		if not expense_account:
			frappe.throw("Set POL Expense Account in Equipment Category")


		# if self.hiring_cost_center:
		#     cost_center = self.hiring_cost_center
		# else:
		# cost_center = get_branch_cc(self.vehicle_branch)


		# ba = get_equipment_ba(self.vehicle)
		# default_ba = get_default_ba()


		gl_entries.append(
			prepare_gl(self, {
				"account": expense_account,
				"debit": flt(self.total_amount_before_gst) if self.apply_gst else flt(self.total_amount),
				"debit_in_account_currency":  flt(self.total_amount_before_gst) if self.apply_gst else flt(self.total_amount),
				"cost_center": self.cost_center,
				"against_voucher": self.name,
				"against_voucher_type": self.doctype,
				# "business_activity": ba
				})
		)
		if self.apply_gst:
			gl_entries.append(
				prepare_gl(self, {
					"account": self.gst_account,
					"debit": flt(self.gst_amount),
					"debit_in_account_currency": flt(self.gst_amount),
					"cost_center": self.cost_center,
					"against_voucher": self.name,
					"against_voucher_type": self.doctype,
					# "business_activity": ba
					})
			)


		gl_entries.append(
			prepare_gl(self, {
				"account": creditor_account,
				"credit": flt(self.total_amount),
				"credit_in_account_currency": flt(self.total_amount),
				"cost_center": self.cost_center,
				"party_type": "Supplier",
				"party": self.supplier,
				"against_voucher": self.name,
				"against_voucher_type": self.doctype,
				# "business_activity": default_ba
				})
		)

		return gl_entries              

	@frappe.whitelist()
	def get_previous_km_reading(self):
		previous_km_reading = 0.0


		previous_km_reading = self.get_previous_km()


		# if not previous_km_reading:
		# 	previous_km_reading = frappe.db.get_value("Equipment", self.equipment, "initial_km_reading")


		# self.previous_km = flt(previous_km_reading)


		return previous_km_reading


	def get_previous_km(self):
		pol_receive = frappe.qb.DocType("POL Receive")


		query = (
			frappe.qb.from_(pol_receive)
			.select(pol_receive.current_km)
			.where(
				(pol_receive.docstatus == 1) &
				(pol_receive.equipment == self.equipment)
			)
			.orderby(pol_receive.creation, order=frappe.qb.desc)
			.limit(1)
		).run(as_dict=True)


		return query[0].get("current_km") if query else 0
		
	@frappe.whitelist()
	def get_pol_advance(self):
		self.set("advances", [])
		
		Advance = frappe.qb.DocType("POL Advance")
		if not self.for_machineries:
			query = (
				frappe.qb.from_(Advance)
				.select(
					Advance.name.as_("reference_name"),
					Advance.advance_amount,
					Advance.balance_amount,
					Advance.posting_date.as_("advance_date"),
				)
				.where(
					(Advance.docstatus == 1)
					& (Advance.balance_amount > 0)
					& (Advance.status == "Paid")
					& (Advance.equipment == self.equipment)
					& (Advance.fuelbook == self.fuelbook)
					& (Advance.company == self.company)
				)
			)
			
		else:
			query = (
				frappe.qb.from_(Advance)
				.select(
					Advance.name.as_("reference_name"),
					Advance.advance_amount,
					Advance.balance_amount,
					Advance.posting_date.as_("advance_date"),
				)
				.where(
					(Advance.docstatus == 1)
					& (Advance.balance_amount > 0)
					& (Advance.status == "Paid")
					& (Advance.equipment == self.equipment)
					& (Advance.supplier == self.supplier)
					& (Advance.company == self.company)
				)
			)
		# frappe.throw(str(query))
		
		advances = query.run(as_dict=True)
		
		if advances:
			self.set("advances", advances)
		else:
			frappe.msgprint("No advances found for this request.", alert=True)
	
	def make_pol_entry(self):
		# if getdate(self.posting_date) <= getdate("2018-03-31"):
        #                 return
		container = frappe.db.get_value("Equipment Type", frappe.db.get_value("Equipment", self.equipment, "equipment_type"), "is_container")
		direct_consumption = frappe.db.get_value("Equipment Type", frappe.db.get_value("Equipment", self.equipment, "equipment_type"), "no_own_tank")
		fuelbook_branch = frappe.db.get_value("Fuelbook", self.fuelbook, "branch")
		if self.branch == fuelbook_branch:
			own = 1
		else:
			own = 0

		con = frappe.new_doc("POL Entry")
		con.flags.ignore_permissions = 1	
		con.equipment = self.equipment
		con.pol_type = self.fuel_type
		con.branch = self.branch
		con.date = self.posting_date
		con.posting_time = self.posting_time
		con.qty = self.total_qty
		con.company = self.company
		con.reference_type = "POL Receive"
		con.reference_name = self.name
		con.is_opening = 0
		con.own_cost_center = own
		if container:
			con.type = "Stock"
			con.save()
		
		if direct_consumption == 0:
			con1 = frappe.new_doc("POL Entry")
			con1.flags.ignore_permissions = 1	
			con1.company = self.company
			con1.equipment = self.equipment
			con1.pol_type = self.fuel_type
			con1.branch = self.branch
			con1.date = self.posting_date
			con1.posting_time = self.posting_time
			con1.qty = self.total_qty
			con1.reference_type = "POL Receive"
			con1.reference_name = self.name
			con1.type = "Receive"
			con1.is_opening = 0
			con1.own_cost_center = own
			con1.save()
			
			if container:
				con2 = frappe.new_doc("POL Entry")
				con2.flags.ignore_permissions = 1	
				con2.company = self.company
				con2.equipment = self.equipment
				con2.pol_type = self.fuel_type
				con2.branch = self.branch
				con2.date = self.posting_date
				con2.posting_time = self.posting_time
				con2.qty = self.total_qty
				con2.reference_type = "POL Receive"
				con2.reference_name = self.name
				con2.type = "Issue"
				con2.is_opening = 0
				con2.own_cost_center = own
				con2.save()


	def cancel_pol_entry(self):
		entries = frappe.get_all(
			"POL Entry",
			filters={"reference_name": self.name},
			pluck="name"
		)

		for entry_name in entries:
			frappe.db.set_value(
				"POL Entry",
				entry_name,
				"is_cancelled",
				1,
				update_modified=False
			)


