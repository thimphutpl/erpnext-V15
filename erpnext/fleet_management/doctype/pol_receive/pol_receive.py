# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, qb, throw
from frappe.utils import flt, cint, cstr, fmt_money, formatdate, nowtime, getdate
from erpnext.custom_utils import check_future_date
from erpnext.controllers.stock_controller import StockController
from erpnext.fleet_management.fleet_utils import get_pol_till, get_pol_till, get_previous_km
from erpnext.accounts.general_ledger import (
	get_round_off_account_and_cost_center,
	make_gl_entries,
	make_reverse_gl_entries,
	merge_similar_entries,
)
from frappe.utils import nowdate, nowtime
from erpnext.accounts.party import get_party_account
from erpnext.fleet_management.report.hsd_consumption_report.fleet_management_report import get_pol_till, get_pol_tills, get_pol_consumed_tills

from erpnext.accounts.utils import get_fiscal_year
from erpnext.custom_utils import check_future_date, get_branch_cc, prepare_gl, prepare_sl, check_budget_available
from erpnext.fleet_management.maintenance_utils import get_without_fuel_hire
class POLReceive(StockController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.pol_receive_item.pol_receive_item import POLReceiveItem
		from frappe.types import DF

		amended_from: DF.Link | None
		amended_froms: DF.Link | None
		book_type: DF.Literal["", "Own", "Common", "Barrel"]
		branch: DF.Link
		company: DF.Link | None
		consumed: DF.Link | None
		cost_center: DF.Link | None
		currency: DF.Link | None
		direct_consumption: DF.Check
		discount_amount: DF.Currency
		equipment: DF.Link | None
		equipment_branch: DF.ReadOnly | None
		equipment_category: DF.Link | None
		equipment_number: DF.Data | None
		equipment_type: DF.ReadOnly | None
		equipment_warehouse: DF.Link | None
		expense_account: DF.Link | None
		fuelbook: DF.Link | None
		fuelbook_branch: DF.ReadOnly | None
		hiring_branch: DF.Data | None
		hiring_cost_center: DF.Data | None
		hiring_warehouse: DF.Data | None
		is_hsd_item: DF.Check
		is_opening: DF.Literal["", "Yes", "No"]
		item_name: DF.Data | None
		items: DF.Table[POLReceiveItem]
		jv: DF.Link | None
		km_difference: DF.Float
		memo_number: DF.Data | None
		mileage: DF.Float
		outstanding_amount: DF.Currency
		own_fb: DF.Data | None
		paid_amount: DF.Currency
		pol_type: DF.Link
		posting_date: DF.Date
		posting_time: DF.Time
		previous_km: DF.Float
		project: DF.ReadOnly | None
		qty: DF.Float
		rate: DF.Currency
		remarks: DF.LongText | None
		serial_and_batch_bundle: DF.Link | None
		stock_uom: DF.Link | None
		supplier: DF.Link
		tank_balance: DF.Float
		tank_capacity: DF.Float
		tanker_balance: DF.Float
		tanker_capacity: DF.Float
		total_amount: DF.Currency
		warehouse: DF.Link | None
	# end: auto-generated types
	def before_save(self):
		if not self.tank_balance:
			self.tank_balance = 0
        # Ensure tank balance does not exceed tank capacity
		if self.book_type == "Own" and flt(self.tank_capacity) < flt(self.tank_balance + self.qty):
			frappe.throw(
                ("Tank capacity ({}) should be greater than or equal to sum of tank balance and quantity ({}).").format(
                    self.tank_capacity, flt(self.tank_balance + self.qty)
                )
            )
		# Ensure tank balance does not exceed tank capacity
		if self.book_type == "Common" and flt(cint(self.tanker_capacity)) < flt(cint(self.tanker_balance + self.qty)):
			frappe.throw(
                ("Tanker capacity ({}) should be greater than or equal to sum of tanker balance and quantity ({}).").format(
                    self.tanker_capacity, flt(self.tanker_balance + self.qty)
                )
            )

	def validate(self):
		check_future_date(self.posting_date)
		self.validate_dc()
		if self.book_type!="Barrel":
			self.validate_warehouse()
			self.validate_data()
		#self.set_warehouse()
		# self.check_on_dry_hire()
		
		# self.validate_posting_time()
		self.validate_uom_is_integer("stock_uom", "qty")
		self.validate_item()
		self.update_posting_date_and_time()

	def on_submit(self):
		self.update_posting_date_and_time()
		self.validate_dc()
		if self.book_type!="Barrel":
			self.validate_data()
		# self.check_on_dry_hire()
		# self.check_budget()

		""" ++++++++++ Ver 2.0.190509 Begins ++++++++++ """
		if self.is_opening == "No" or self.is_opening == "" and self.book_type!="Barrel":
			# self.update_stock_ledger()
			self.validate_advance_amount()
			self.update_pol_advance()
			self.make_gl_entries()
		self.make_pol_entry()
		if self.book_type=="Barrel":
			self.post_journal_entry()
		# self.repost_future_sle_and_gle()
		""" ++++++++++ Ver 2.0.190509 Ends ++++++++++++ """
	
	# def before_cancel(self):
	# 	self.delete_pol_entry()

	def on_cancel(self):
		# if getdate(self.posting_date) > getdate("2018-03-31") and (self.is_opening == "No" or self.is_opening == "") or self.is_opening == "Yes" and self.book_type == "Common":
		# 	self.update_stock_ledger()
		if self.is_opening != "Yes" and self.book_type!="Barrel":
			self.make_gl_entries_on_cancel()
		# self.repost_future_sle_and_gle()
		""" ++++++++++ Ver 2.0.190509 Ends ++++++++++++ """
		self.ignore_linked_doctypes = (
			"GL Entry",
			"Payment Ledger Entry",
			"Stock Ledger Entry",
			"Repost Item Valuation",
			"Serial and Batch Bundle",
			"HSD Payment",
			"POL Entry"
		)
		if self.book_type!="Barrel":
			self.update_pol_advance()
		if self.book_type =="Barrel":
			docstatus = frappe.db.get_value("Journal Entry", self.jv, "docstatus")
			if docstatus ==1:
				frappe.throw("Cancel the Journal Entry " + str(self.jv) + " and proceed.")
			if docstatus==0:
				frappe.db.sql("""delete from `tabJournal Entry` where name='{name}'""".format(name=self.jv))
		self.db_set("jv", None)
		self.make_pol_entry(cancel=True)
	def update_posting_date_and_time(self):
		self.posting_date = nowdate()
		self.posting_time =nowtime()
	def validate_advance_amount(self):
		allocated_amount = 0
		for raw in self.items:
			allocated_amount = allocated_amount + raw.allocated_amount
		if self.total_amount != allocated_amount:
			frappe.throw("Total Amount can not be greater than Advance amount difference is "+str(self.total_amount - allocated_amount))

	def update_pol_advance(self):
		if self.docstatus == 2 :
			for item in self.items:
				doc = frappe.get_doc("POL Advance", {'name':item.pol_advance})
				doc.adjusted_amount = flt(doc.adjusted_amount) - flt(item.allocated_amount)
				doc.balance_amount  = flt(doc.amount) - flt(doc.adjusted_amount)
				doc.save(ignore_permissions=True)
			return
		for item in self.items:
			doc = frappe.get_doc("POL Advance", {'name':item.pol_advance})
			doc.balance_amount  = flt(item.balance_amount) - flt(item.allocated_amount)
			doc.adjusted_amount = flt(doc.adjusted_amount) + flt(item.allocated_amount)
			doc.save(ignore_permissions=True)
	# Fetch equipment_type from Equipment
	def validate_dc(self):
		equipment_type = frappe.db.get_value("Equipment", self.equipment, "equipment_type")
		if equipment_type:
			result = frappe.db.get_value("Equipment Type", equipment_type, ["is_container", "no_own_tank"])
			
			if result:
				is_container, no_own_tank = result
			else:
				is_container = 0
				no_own_tank = 0
		else:
			is_container = 0
			no_own_tank = 0

		if not self.direct_consumption and not is_container and self.book_type!="Barrel":
			frappe.throw("Non 'Direct Consumption' Receive POL is allowed only for Container Equipments")

		if self.direct_consumption and no_own_tank:
			frappe.throw("Direct Consumption not permitted for Equipments without own Tank")
	def validate_warehouse(self):
		self.validate_warehouse_branch(self.warehouse, self.branch)
		self.validate_warehouse_branch(self.equipment_warehouse, self.equipment_branch)
		if self.hiring_branch:
			self.validate_warehouse_branch(self.hiring_warehouse, self.hiring_branch)

	def set_warehouse(self):
		cc = get_branch_cc(self.equipment_branch)
		equipment_warehouse = frappe.db.get_value("Cost Center", cc, "warehouse")
		if not equipment_warehouse:
			frappe.throw("No Warehouse is linked with Cost Center <b>" + str(cc) + "</b>")
		self.equipment_warehouse = equipment_warehouse	

	def validate_data(self):
		if not self.warehouse:
			frappe.throw("Warehouse is Mandatory. Set the Warehouse in Cost Center")
		if self.branch != self.fuelbook_branch:
			frappe.throw("Transaction Branch and Fuelbook Branch should be same")
		if self.book_type == "Own":
			if self.fuelbook != frappe.db.get_value("Equipment", self.equipment, "fuelbook"):
				frappe.throw("Fuelbook (<b>" + str(self.fuelbook) + "</b>) is not registered to <b>" + str(self.equipment) + "</b>")

	def validate_item(self):
		is_stock, is_hsd, is_pol = frappe.db.get_value("Item", self.pol_type, ["is_stock_item", "is_hsd_item", "is_pol_item"])
		if not is_stock:
			frappe.throw(str(self.item_name) + " is not a stock item")

		if not is_hsd and not is_pol:
			frappe.throw(str(self.item_name) + " is not a HSD/POL item")

	def check_budget(self):
		if self.hiring_cost_center:
			cc = self.hiring_cost_center
		else:
			cc = get_branch_cc(self.equipment_branch)
		account = frappe.db.get_value("Equipment Category", self.equipment_category, "budget_account")
		if not self.is_hsd_item:
			account = frappe.db.get_value("Item Default", {'parent': self.pol_type}, "expense_account")

	# Update the Committedd Budget for checking budget availability
	##
	def consume_budget(self, cc, account):
		bud_obj = frappe.get_doc({
			"doctype": "Committed Budget",
			"account": account,
			"cost_center": cc,
			"po_no": self.name,
			"po_date": self.posting_date,
			"amount": self.total_amount,
			"item_code": self.pol_type,
			"poi_name": self.name,
			"date": frappe.utils.nowdate()
			})
		bud_obj.flags.ignore_permissions = 1
		bud_obj.submit()

		consume = frappe.get_doc({
			"doctype": "Consumed Budget",
			"account": account,
			"cost_center": cc,
			"po_no": self.name,
			"po_date": self.posting_date,
			"amount": self.total_amount,
			"pii_name": self.name,
			"item_code": self.pol_type,
			"com_ref": bud_obj.name,
			"date": frappe.utils.nowdate()})
		consume.flags.ignore_permissions=1
		consume.submit()

		""" ++++++++++ Ver 2.0.190509 Begins ++++++++++ """
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

	def update_stock_ledger(self):
		# Stock entry for direct_consumption is disabled due to MAP related issues
		if self.direct_consumption:
			return		
		if self.hiring_warehouse:
			wh = self.hiring_warehouse
		else:
			wh = self.equipment_warehouse

		sl_entries = []
		sl_entries.append(self.get_sl_entries(self, {
					"item_code": self.pol_type,
					"actual_qty": flt(self.qty), 
					"warehouse": wh, 
					"incoming_rate": round(flt(self.total_amount) / flt(self.qty) , 2)
				}))

		if self.docstatus == 2:
			sl_entries.reverse()

		self.make_sl_entries(sl_entries, self.amended_from and 'Yes' or 'No')


	def get_gl_entries(self, warehouse_account):
		gl_entries = []
		
		creditor_account = frappe.db.get_value("Company", self.company, "default_payable_account")
		if not creditor_account:
			frappe.throw("Set Default Payable Account in Company")

		expense_account = self.get_expense_account()

		if self.hiring_cost_center:
			cost_center = self.hiring_cost_center
		else:
			cost_center = get_branch_cc(self.equipment_branch)

		gl_entries.append(
			self.get_gl_dict({"account": expense_account,
					 "debit": flt(self.total_amount),
					 "debit_in_account_currency": flt(self.total_amount),
					 "cost_center": cost_center,
			})
		)

		gl_entries.append(
			self.get_gl_dict({"account": creditor_account,
					 "credit": flt(self.total_amount),
					 "credit_in_account_currency": flt(self.total_amount),
					 "cost_center": self.cost_center,
					 "party_type": "Supplier",
					 "party": self.supplier,
					 "against_voucher": self.name,
										 "against_voucher_type": self.doctype,
			})
		)
		# frappe.msgprint(self.hiring_branch)
		if self.hiring_branch:
			comparing_branch = self.hiring_branch
		else:
			comparing_branch = self.equipment_branch

		if comparing_branch != self.fuelbook_branch:
			ic_account = frappe.db.get_single_value("Accounts Settings", "intra_company_account")
			if not ic_account:
				frappe.throw("Setup Intra-Company Account in Accounts Settings")

			customer_cc = get_branch_cc(comparing_branch)

			gl_entries.append(
				self.get_gl_dict({"account": ic_account,
						 "credit": flt(self.total_amount),
						 "credit_in_account_currency": flt(self.total_amount),
						 "cost_center": customer_cc,
				})
			)

			gl_entries.append(
				self.get_gl_dict({"account": ic_account,
						 "debit": flt(self.total_amount),
						 "debit_in_account_currency": flt(self.total_amount),
						 "cost_center": self.cost_center,
				})
			)

		return gl_entries
		
		""" ++++++++++ Ver 2.0.190509 Ends ++++++++++++ """

	def get_expense_account(self):
		if self.direct_consumption or getdate(self.posting_date) <= getdate("2018-03-31"):
			if self.is_hsd_item:
				expense_account = frappe.db.get_value("Equipment Category", self.equipment_category, "budget_account")
			else:
				expense_account = frappe.db.get_value("Item Default", {'parent': self.pol_type}, "expense_account")

			if not expense_account:
				frappe.throw("Set Budget Account in Equipment Category or Item Master")		
		else:
			if self.hiring_warehouse:
				wh = self.hiring_warehouse
			else:
				wh = self.equipment_warehouse
			# expense_account = frappe.db.get_value("Account", {"account_type": "Stock", "warehouse": wh}, "name")
			expense_account = frappe.db.get_value("Warehouse", {"name": wh}, "account")
			if not expense_account:
					frappe.throw(str(wh) + " is not linked to any account.")

		return expense_account

	##
	# Cancel budget check entry
	##
	def cancel_budget_entry(self):
		frappe.db.sql("delete from `tabCommitted Budget` where po_no = %s", self.name)
		frappe.db.sql("delete from `tabConsumed Budget` where po_no = %s", self.name)

	##
	# make necessary journal entry
	##
	def post_journal_entry(self):
		barrel_account = frappe.db.get_value("Company",self.company,"fuel_stock_account")
		expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		if not expense_bank_account:
			frappe.throw("No Default Bank Account set in Branch")
		if not barrel_account:
			frappe.throw("Please set fuel stock account in company")

		if expense_bank_account and barrel_account:
			je = frappe.new_doc("Journal Entry")
			je.flags.ignore_permissions = 1 
			je.title = "POL (" + self.pol_type + " for " + self.branch + ")"
			je.voucher_type = 'Bank Entry'
			je.naming_series = 'Bank Payment Voucher'
			je.remark = 'Payment against : ' + self.name
			je.posting_date = self.posting_date
			je.branch = self.branch

			je.append("accounts", {
					"account": barrel_account,
					"cost_center": self.cost_center,
					"reference_type": "POL Receive",
					"reference_name": self.name,
					"debit_in_account_currency": flt(self.total_amount),
					"debit": flt(self.total_amount),
				})

			je.append("accounts", {
					"account": expense_bank_account,
					"cost_center": self.cost_center,
					"party_type": "Supplier",
					"party": self.supplier,
					"credit_in_account_currency": flt(self.total_amount),
					"credit": flt(self.total_amount),
				})

			je.insert()
			self.db_set("jv", je.name)
			frappe.msgprint("Journal Entry "+str(je.name)+ "Posted for Bank Payment")
		else:
			frappe.throw("Couldnt Post Journal Entry")

	def make_pol_entry(self, cancel=False):
		if self.book_type=="Barrel":
			cond ="and is_barrel = 1"
		else:
			cond ="and equipment='{equipment}'".format(equipment=self.equipment)
		balance_qty = frappe.db.sql("""select qty, rate, amount
			from `tabPOL Entry` 
			where branch='{branch}'
			and item ='{item}'
			{cond}
			order by timestamp(posting_date, posting_time) desc
			limit 1
			""".format(branch=self.branch, item=self.pol_type, cond=cond), as_dict=True)
		b_qty = self.qty
		b_rate= self.rate
		total_amount = self.total_amount
		for raw in balance_qty:
			if not cancel:
				b_qty = raw.qty + self.qty
				total_amount = raw.amount + self.total_amount
				b_rate = total_amount / b_qty
			else:
				b_qty = raw.qty - self.qty
				total_amount = raw.amount - self.total_amount
				b_rate = total_amount / b_qty
				if row.qty < self.qty:
					frappe.throw("Cannot cancel this POL Receive!!! POL Issue has been made agains this receive")

		con = frappe.new_doc("POL Entry")
		con.flags.ignore_permissions = 1
		if self.pol_type !="Barrel":	
			con.equipment = self.equipment
		else:
			con.is_barrel = 1
		con.book_type = self.book_type
		con.item = self.pol_type
		con.branch = self.branch
		con.posting_date = nowdate()
		con.posting_time = nowtime()
		con.qty = b_qty
		con.rate = b_rate
		con.amount = total_amount
		con.reference_type = "POL Receive"
		con.reference_name = self.name
		con.is_opening = 0
		con.submit()

			# name = frappe.db.get_value("POL Entry",{"reference_name":self.name},"name")
			# frappe.db.sql("""delete from `tabPOL Entry` where name='{name}'""".format(name=name))
		# if self.direct_consumption:
		# 	con1 = frappe.new_doc("POL Entry")
		# 	con1.flags.ignore_permissions = 1	
		# 	con1.equipment = self.equipment
		# 	con1.pol_type = self.pol_type
		# 	con1.branch = self.equipment_branch
		# 	con1.posting_date = self.posting_date
		# 	con1.posting_time = self.posting_time
		# 	con1.qty = self.qty
		# 	con1.reference_type = "POL Receive"
		# 	con1.reference_name = self.name
		# 	con1.type = "Receive"
		# 	con1.is_opening = 0
		# 	con1.own_cost_center = own
		# 	con1.submit()
			
		# 	if container:
		# 		con2 = frappe.new_doc("POL Entry")
		# 		con2.flags.ignore_permissions = 1	
		# 		con2.equipment = self.equipment
		# 		con2.pol_type = self.pol_type
		# 		con2.branch = self.equipment_branch
		# 		con2.posting_date = self.posting_date
		# 		con2.posting_time = self.posting_time
		# 		con2.qty = self.qty
		# 		con2.reference_type = "POL Receive"
		# 		con2.reference_name = self.name
		# 		con2.type = "Issue"
		# 		con2.is_opening = 0
		# 		con2.own_cost_center = own
		# 		con2.submit()


	def delete_pol_entry(self):
		frappe.db.sql("delete from `tabPOL Entry` where reference_name = %s", self.name)

	@frappe.whitelist()
	def populate_child_table(self):
		pol_exp = qb.DocType("POL Advance")
		je = qb.DocType("Journal Entry")
		data = []
		if not self.equipment or not self.supplier:
			frappe.throw("Either equipment or Supplier is missing")

		query = qb.from_(pol_exp).select(pol_exp.name, pol_exp.amount, pol_exp.balance_amount)
		if self.book_type =="Own":
			query = query.where(
				(pol_exp.docstatus == 1) &
				(pol_exp.balance_amount > 0) &
				(pol_exp.entry_date <= self.posting_date) &
				(pol_exp.equipment == self.equipment) &
				(pol_exp.party == self.supplier) &
				(pol_exp.fuel_book == self.fuelbook)
			)
		else:
			query = query.where(
				(pol_exp.docstatus == 1) &
				(pol_exp.balance_amount > 0) &
				(pol_exp.party == self.supplier) &
				(pol_exp.entry_date <= self.posting_date) &
				(pol_exp.fuel_book == self.fuelbook) &
				(pol_exp.equipment == self.equipment) &
				(pol_exp.book_type =="Common")
			)
		
		query = query.orderby(pol_exp.entry_date)
		data = query.run(as_dict=True)
		
		if not data:
			frappe.throw("NO POL Advance Found against Equipment {}. Make sure Journal Entries are submitted".format(self.equipment))
		
		self.set('items', [])
		allocated_amount = self.total_amount
		total_amount_adjusted = 0
		
		for d in data:
			row = self.append('items', {})
			row.pol_advance = d.name
			row.amount = d.amount
			row.balance_amount = d.balance_amount
			
			if row.balance_amount >= allocated_amount:
				row.allocated_amount = allocated_amount
				total_amount_adjusted += flt(row.allocated_amount)
				allocated_amount = 0
			elif row.balance_amount < allocated_amount:
				row.allocated_amount = row.balance_amount
				total_amount_adjusted += flt(row.allocated_amount)
				allocated_amount = flt(allocated_amount) - flt(row.balance_amount)
			
			row.balance = flt(row.balance_amount) - flt(row.allocated_amount)
# Tank Balance
@frappe.whitelist()
def tank_balance(pol_receive):
	t, m = frappe.db.get_value("POL Receive", pol_receive, ['equipment_type', 'equipment_number'])
	data = frappe.db.sql("select qty from `tabPOL Receive` where equipment_type = %s and equipment_number = %s", (t, m), as_dict=True)
	if not data:
		frappe.throw("Setup yardstick for " + str(m))
	return data

@frappe.whitelist()
def fetch_tank_balance(equipment):
    if not equipment:
        frappe.throw("Equipment is required to fetch Tank Balance.")

    # Fetch the qty from POL Receive based on equipment
    qty = frappe.db.get_value("POL Receive", {"equipment": equipment}, "qty")
    
    if qty is None:
        frappe.throw(f"No POL Receive entry found for the selected equipment: {equipment}")

    return qty	

@frappe.whitelist()
def get_equipment_data(equipment, all_equipment=0, branch=None):
	# frappe.throw("Get Tank")
	data = []

	query = """
		SELECT e.name, e.branch, e.registration_number, e.hsd_type, e.equipment_type
		FROM `tabEquipment` e
		JOIN `tabEquipment Type` et ON e.equipment_type = et.name
	"""

	if not all_equipment:
		query += " WHERE et.is_container = 1"
	else:
		query += " WHERE 1=1"

	if branch:
		query += " AND e.branch = %(branch)s"
	if equipment:
		query += " AND e.name = %(equipment)s"

	query += " ORDER BY e.branch"

	items = frappe.db.sql("""
		SELECT item_code, item_name, stock_uom 
		FROM `tabItem`
		WHERE is_hsd_item = 1 AND disabled = 0
	""", as_dict=True)

	equipment_details = frappe.db.sql(query, {
		'branch': branch,
		'equipment': equipment
	}, as_dict=True)

	for eq in equipment_details:
		for item in items:
			received = issued = 0
			if all_equipment:
				if eq.hsd_type == item.item_code:
					received = get_pol_tills("Receive", eq.name, item.item_code)
					issued = get_pol_consumed_tills(eq.name,)
			else:
				received = get_pol_tills("Stock", eq.name, item.item_code)
				issued = get_pol_tills("Issue", eq.name, item.item_code)
						
			
			if received or issued:
				data.append({
					'received': received,
					'issued': issued,
					'balance': flt(received) - flt(issued)
				})
	

	return data							

@frappe.whitelist()
def get_balance_details(book_type, tanker=None, equipment=None, posting_date=None, pol_type=None):
    """
    Fetch the balance details for tanker or equipment based on the book_type.
    """
    if not posting_date:
        frappe.throw("Posting Date is mandatory.")

    data = {}  # Initialize data dictionary to store results

    if book_type == "Common" and equipment:
        # Fetch tanker balances
        received_till = get_pol_tills("Stock", equipment, posting_date, pol_type)
        issue_till = get_pol_tills("Issue", equipment, posting_date, pol_type)
        tanker_balance = flt(received_till) - flt(issue_till)
        data = {"tanker_balance": tanker_balance, "tank_balance": 0}

    elif book_type == "Own" and equipment:
        # Fetch equipment balances
        received_till = get_pol_tills("Receive", equipment, posting_date, pol_type)
        issue_till = get_pol_tills("Issue", equipment, posting_date, pol_type)
        tank_balance = flt(received_till) - flt(issue_till)
        data = {"tanker_balance": 0, "tank_balance": tank_balance}

    else:
        frappe.throw("Invalid inputs. Please ensure the correct book_type, tanker, or equipment is provided.")

    # Optional: If you want to include detailed balance data
    if received_till or issue_till:
        data.update({
            'received': received_till,
            'issued': issue_till,
            'balance': flt(received_till) - flt(issue_till)
        })

    return data

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles: 
		return

	return """(
		`tabPOL Receive`.owner = '{user}'
		or
		exists(select 1
			from `tabEmployee` as e
			where e.branch = `tabPOL Receive`.branch
			and e.user_id = '{user}')
		or
		exists(select 1
			from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
			where e.user_id = '{user}'
			and ab.employee = e.name
			and bi.parent = ab.name
			and bi.branch = `tabPOL Receive`.branch)
	)""".format(user=user)
 
@frappe.whitelist()
def get_filtered_equipment(doctype, txt, searchfield, start, page_len, filters):
    if not filters:
        return []

    return frappe.db.sql("""
        SELECT e.name, e.registration_number
        FROM `tabEquipment` e 
        INNER JOIN `tabEquipment Type` et ON e.equipment_type = et.name 
        WHERE et.is_container = 1 
        AND e.branch = %(branch)s
    """, {
        "branch": filters["branch"]
    })