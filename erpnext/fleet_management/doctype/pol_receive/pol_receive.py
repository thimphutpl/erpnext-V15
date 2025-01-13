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
from erpnext.accounts.party import get_party_account
from erpnext.fleet_management.report.hsd_consumption_report.fleet_management_report import get_pol_tills, get_pol_consumed_tills, get_pol_till_tanker, get_pol_consumed_till_tanker

from frappe.desk.reportview import get_match_cond
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
		book_type: DF.Literal["", "Own", "Common"]
		branch: DF.Link
		company: DF.Link
		consumed: DF.Link | None
		cost_center: DF.Link | None
		direct_consumption: DF.Check
		discount_amount: DF.Currency
		equipment: DF.Link | None
		equipment_branch: DF.ReadOnly | None
		equipment_category: DF.ReadOnly | None
		equipment_number: DF.Data | None
		equipment_type: DF.ReadOnly | None
		equipment_warehouse: DF.Link
		expense_account: DF.Link | None
		fuelbook: DF.Link | None
		fuelbook_branch: DF.ReadOnly | None
		hiring_branch: DF.Data | None
		hiring_cost_center: DF.Data | None
		hiring_warehouse: DF.Data | None
		is_hsd_item: DF.Check
		is_opening: DF.Literal["", "Yes"]
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
		qty: DF.Float
		rate: DF.Currency
		remarks: DF.LongText | None
		stock_uom: DF.Link | None
		supplier: DF.Link
		tank_balance: DF.Data | None
		tank_capacity: DF.ReadOnly | None
		tank_warehouse: DF.Link | None
		tanker: DF.Link | None
		tanker_balance: DF.Data | None
		tanker_branch: DF.ReadOnly | None
		tanker_capacity: DF.ReadOnly | None
		tanker_category: DF.ReadOnly | None
		tanker_number: DF.Data | None
		tanker_quantity: DF.Float
		tanker_type: DF.ReadOnly | None
		total_amount: DF.Currency
		warehouse: DF.Link
	# end: auto-generated types
	def before_save(self):
        # Ensure tank balance does not exceed tank capacity
		if self.book_type == "Own" and flt(self.tank_capacity) < flt(self.tank_balance + self.qty):
			frappe.throw(
                ("Tank capacity ({}) should be greater than or equal to sum of tank balance and quantity ({}).").format(
                    self.tank_capacity, flt(self.tank_balance + self.qty)
                )
            )

		# Ensure tank balance does not exceed tank capacity
		if self.book_type == "Common" and flt(self.tanker_capacity) < flt(self.tanker_balance + qty):
			frappe.throw(
                ("Tanker capacity ({}) should be greater than or equal to sum of tanker balance and quantity ({}).").format(
                    self.tanker_capacity, flt(self.tanker_balance + self.qty)
                )
            )	
			
	def validate(self):
		check_future_date(self.posting_date)
		# self.validate_dc()
		self.validate_warehouse()
		#self.set_warehouse()
		self.check_on_dry_hire()
		self.validate_data()
		self.validate_posting_time()
		self.validate_uom_is_integer("stock_uom", "qty")
		self.validate_item()

	def on_submit(self):
		# self.validate_dc()
		self.validate_data()
		self.check_on_dry_hire()
		self.check_budget()

		# # Skip GL Entries if is_opening is "Yes"
		# if self.is_opening == "Yes":
		# 	frappe.msgprint(
		# 		("Skipping GL entries and stock ledger updates since this is an Opening Entry."),
		# 		alert=True
		# 	)
		# 	return

		# if getdate(self.posting_date) > getdate("2018-03-31"):
		# 	self.update_stock_ledger()
		# """ ++++++++++ Ver 2.0.190509 Begins ++++++++++ """
		# # Ver 2.0.190509, Following method commented by SHIV on 2019/05/20 
		# #self.update_general_ledger(1)

		# # Ver 2.0.190509, Following method added by SHIV on 2019/05/20
		# self.make_gl_entries()
		# """ ++++++++++ Ver 2.0.190509 Ends ++++++++++++ """
		
		# self.make_pol_entry()

		

		""" ++++++++++ Ver 2.0.190509 Begins ++++++++++ """
		if getdate(self.posting_date) > getdate("2018-03-31") and self.is_opening == "No" or self.is_opening == "":
			self.update_stock_ledger()
			self.make_gl_entries()

		# Skip GL Entries if is_opening is "Yes"
		elif self.is_opening == "Yes" and self.book_type == "Common":
			self.update_stock_ledger()
		else:
			pass
		
		self.make_pol_entry()
		""" ++++++++++ Ver 2.0.190509 Ends ++++++++++++ """

		#New code add on 07/01/2025
		# if cint(self.is_opening) == 0:
		# 	self.update_stock_ledger()
		# 	# if self.use_common_fuelbook and not self.direct_consumption:
		# 	self.make_gl_entries()
		# self.make_pol_entry()

		# if cint(self.is_opening) == 'Yes':
		# 	return
	
	def before_cancel(self):
		self.delete_pol_entry()

	def on_cancel(self):
		if getdate(self.posting_date) > getdate("2018-03-31") and self.is_opening == "No" or self.is_opening == "Yes" and self.book_type == "Common":
			self.update_stock_ledger()
		""" ++++++++++ Ver 2.0.190509 Begins ++++++++++ """
		# Ver 2.0.190509, Following method commented by SHIV on 2019/05/20 
		#self.update_general_ledger(1)

		# Ver 2.0.190509, Following method added by SHIV on 2019/05/20
		if self.is_opening == "No":
			self.make_gl_entries_on_cancel()
		""" ++++++++++ Ver 2.0.190509 Ends ++++++++++++ """
		self.ignore_linked_doctypes = (
			"GL Entry",
			"Stock Ledger Entry",
			"Repost Item Valuation",
			"Serial and Batch Bundle",
		)
		docstatus = frappe.db.get_value("Journal Entry", self.jv, "docstatus")
		if docstatus and docstatus != 2:
			frappe.throw("Cancel the Journal Entry " + str(self.jv) + " and proceed.")

		self.db_set("jv", None)

		# self.cancel_budget_entry() #jai, this should handle at General Ledger process

		#New code add on 07/01/2025
		# if cint(self.is_opening) == 0:
		# 	self.update_stock_ledger()
		# self.delete_pol_entry()

	# def validate_dc(self):
	# 	if self.book_type == "Common":
	# 		is_container, no_own_tank = frappe.db.get_value("Equipment Type", frappe.db.get_value("Equipment", self.tanker, "equipment_type") , ["is_container", "no_own_tank"])
	# 	else:	
	# 		is_container, no_own_tank = frappe.db.get_value("Equipment Type", frappe.db.get_value("Equipment", self.equipment, "equipment_type") , ["is_container", "no_own_tank"])

	# 	if not self.direct_consumption and not is_container:
	# 		frappe.throw("Non 'Direct Consumption' Receive POL is allowed only for Container Equipments")

	# 	if self.direct_consumption and no_own_tank:
	# 					frappe.throw("Direct Consumption not permitted for Equipments without own Tank")

	# def validate_dc(self):
	# 	is_container, no_own_tank = frappe.db.get_value("Equipment Type", frappe.db.get_value("Equipment", self.equipment, "equipment_type") , ["is_container", "no_own_tank"])
	# 	if not self.direct_consumption and not is_container:
	# 		frappe.throw("Non 'Direct Consumption' Receive POL is allowed only for Container Equipments")

	# 	if self.direct_consumption and no_own_tank:
	# 					frappe.throw("Direct Consumption not permitted for Equipments without own Tank")

	def validate_warehouse(self):
				self.validate_warehouse_branch(self.warehouse, self.branch)
				if self.book_type == "Own":
					self.validate_warehouse_branch(self.equipment_warehouse, self.equipment_branch)
				# if self.book_type == "Common":
				# 	self.validate_warehouse_branch(self.tanker_warehouse, self.tanker_branch)	
				if self.hiring_branch:
						self.validate_warehouse_branch(self.hiring_warehouse, self.hiring_branch)

	def set_warehouse(self):
		cc = get_branch_cc(self.equipment_branch)
		equipment_warehouse = frappe.db.get_value("Cost Center", cc, "warehouse")
		if not equipment_warehouse:
			frappe.throw("No Warehouse is linked with Cost Center <b>" + str(cc) + "</b>")
		self.equipment_warehouse = equipment_warehouse	

	def check_on_dry_hire(self):
				record = get_without_fuel_hire(self.equipment, self.posting_date, self.posting_time)
				if record:
						data = record[0]
						self.hiring_cost_center = data.cc
						self.hiring_branch =  data.br
						self.hiring_warehouse = frappe.db.get_value("Cost Center", data.cc, "warehouse")
				else:
						self.hiring_cost_center = None
						self.hiring_branch =  None
						self.hiring_warehouse = None

	def validate_data(self):
		# if self.book_type == "Common":
		# 	# return
		# 	if not self.fuelbook_branch or not self.tanker_branch:
		# 		frappe.throw("Fuelbook and Tank Branch are mandatory")
		# else:
		# 	if not self.fuelbook_branch or not self.equipment_branch:
		# 		frappe.throw("Fuelbook and Equipment Branch are mandatory")

		# if self.book_type == "Common" and flt(self.rate) <= 0 and flt(self.tanker_quantity) <= 0:
		# 	frappe.throw("Tanker Quantity and Rate should be greater than 0")
		# elif self.book_type == "Own" and flt(self.qty) <= 0 or flt(self.rate) <= 0:
		# 	frappe.throw("Own Quantity and Rate should be greater than 0")	

		# if flt(self.qty) <= 0 or flt(self.rate) <= 0:
		# 	frappe.throw("Quantity and Rate should be greater than 0")

		if not self.warehouse:
			frappe.throw("Warehouse is Mandatory. Set the Warehouse in Cost Center")

		# if not self.equipment_category:
		# 	frappe.throw("Equipment Category Missing")
		
		# if self.book_type == "Common":
		# 	# return
		# 	if not self.tanker_category:
		# 		frappe.throw("Fuelbook and Tank Branch are mandatory")
		# else:
		# 	if not self.equipment_category:
		# 		frappe.throw("Equipment Category Missing")

		if self.branch != self.fuelbook_branch:
			frappe.throw("Transaction Branch and Fuelbook Branch should be same")
	
		if self.book_type == "Own":
			if self.fuelbook != frappe.db.get_value("Equipment", self.equipment, "fuelbook"):
				frappe.throw("Fuelbook (<b>" + str(self.fuelbook) + "</b>) is not registered to <b>" + str(self.equipment) + "</b>")

		# #New
		# if flt(self.tanker_quantity) <= 0 or flt(self.rate) <= 0:
		# 	return
		# if flt(self.qty) <= 0 or flt(self.rate) <= 0:
		# 	frappe.throw("Quantity and Rate should be greater than 0")		

	def validate_item(self):
		is_stock, is_hsd, is_pol = frappe.db.get_value("Item", self.pol_type, ["is_stock_item", "is_hsd_item", "is_pol_item"])
		if not is_stock:
			frappe.throw(str(self.item_name) + " is not a stock item")

		if not is_hsd and not is_pol:
			frappe.throw(str(self.item_name) + " is not a HSD/POL item")

	def check_budget(self):
		# if self.book_type == "Common":
		# 	return
		# if cint(self.is_opening) == 1:
		# 	return
		
		if self.hiring_cost_center:
			cc = self.hiring_cost_center
		# elif self.book_type == "Common":
		# 	cc = get_branch_cc(self.tanker_branch)	
		else:
			cc = get_branch_cc(self.equipment_branch)
		account = frappe.db.get_value("Equipment Category", self.tanker_category, "budget_account")	
		account = frappe.db.get_value("Equipment Category", self.equipment_category, "budget_account")
		if not self.is_hsd_item:
			account = frappe.db.get_value("Item Default", {'parent': self.pol_type}, "expense_account")

		# jai, its handle from General Ledger process, and have to mention in Budget Setting
		# check_budget_available(cc, account, self.posting_date, self.total_amount)
		# self.consume_budget(cc, account)

	##
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
		# Ver 2.0.190509, Following method added by SHIV on 2019/05/14
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

		# Ver 2.0.190509, Following method commented by SHIV on 2019/05/14
		"""
	def update_stock_ledger(self):
		if self.direct_consumption:
			return
		if self.hiring_warehouse:
						wh = self.hiring_warehouse
				else:
						wh = self.equipment_warehouse

		sl_entries = []
		sl_entries.append(prepare_sl(self, 
				{
					"actual_qty": flt(self.qty), 
					"warehouse": wh, 
					"incoming_rate": round(flt(self.total_amount) / flt(self.qty) , 2)
				}))

		if self.direct_consumption:
			sl_entries.append(prepare_sl(self,
					{
						"actual_qty": -1 * flt(self.qty), 
						"warehouse": wh, 
						"incoming_rate": 0
					}))
 
		if self.docstatus == 2:
			sl_entries.reverse()

		self.make_sl_entries(sl_entries, self.amended_from and 'Yes' or 'No')
	"""

	def get_gl_entries(self, warehouse_account):
		gl_entries = []
		
		creditor_account = frappe.db.get_value("Company", self.company, "default_payable_account")
		if not creditor_account:
			frappe.throw("Set Default Payable Account in Company")

		expense_account = self.get_expense_account()

		if self.hiring_cost_center:
			cost_center = self.hiring_cost_center
		# elif self.book_type == "Common":
		# 	cost_center = get_branch_cc(self.tanker_branch)	
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
		# elif self.book_type == "Common":
		# 	comparing_branch = self.tanker_branch		
		else:
			comparing_branch = self.equipment_branch

		if comparing_branch != self.fuelbook_branch:
			ic_account = frappe.db.get_single_value("Accounts Settings", "intra_company_account")
			if not ic_account:
				frappe.throw("Setup Intra-Company Account in Accounts Settings")

			if self.book_type == "Common":
				customer_cc = get_branch_cc(comparing_branch)
			else:	
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
		
		# Ver 2.0.190509, following code commented by SHIV on 2019/05/21
		"""
	def update_general_ledger(self, post=None):
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
			prepare_gl(self, {"account": expense_account,
					 "debit": flt(self.total_amount),
					 "debit_in_account_currency": flt(self.total_amount),
					 "cost_center": cost_center,
					})
			)

		gl_entries.append(
			prepare_gl(self, {"account": creditor_account,
					 "credit": flt(self.total_amount),
					 "credit_in_account_currency": flt(self.total_amount),
					 "cost_center": self.cost_center,
					 "party_type": "Supplier",
					 "party": self.supplier,
					 "against_voucher": self.name,
										 "against_voucher_type": self.doctype,
					})
			)

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
				prepare_gl(self, {"account": ic_account,
						 "credit": flt(self.total_amount),
						 "credit_in_account_currency": flt(self.total_amount),
						 "cost_center": customer_cc,
						})
				)

			gl_entries.append(
				prepare_gl(self, {"account": ic_account,
						 "debit": flt(self.total_amount),
						 "debit_in_account_currency": flt(self.total_amount),
						 "cost_center": self.cost_center,
						})
				)

		from erpnext.accounts.general_ledger import make_gl_entries
		if post:
			make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=False)
		else:
			return gl_entries
	"""
		""" ++++++++++ Ver 2.0.190509 Ends ++++++++++++ """

	def get_expense_account(self):
		if self.direct_consumption or getdate(self.posting_date) <= getdate("2024-03-31"):
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
		veh_cat = frappe.db.get_value("Equipment", self.equipment, "equipment_category")
		if veh_cat:
			if veh_cat == "Pool Vehicle":
				pol_account = frappe.db.get_single_value("Maintenance Accounts Settings", "pool_vehicle_pol_expenses")
			else:
				pol_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_pol_expense_account")
		else:
			frappe.throw("Can not determine machine category")
		#expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		expense_bank_account = frappe.db.get_value("Company", frappe.defaults.get_user_default("Company"), "default_payable_account")
		if not expense_bank_account:
			frappe.throw("No Default Payable Account set in Company")

		if expense_bank_account and pol_account:
			je = frappe.new_doc("Journal Entry")
			je.flags.ignore_permissions = 1 
			je.title = "POL (" + self.pol_type + " for " + self.equipment_number + ")"
			je.voucher_type = 'Bank Entry'
			je.naming_series = 'Bank Payment Voucher'
			je.remark = 'Payment against : ' + self.name;
			je.posting_date = self.posting_date
			je.branch = self.branch

			je.append("accounts", {
					"account": pol_account,
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
		else:
			frappe.throw("Define POL expense account in Maintenance Setting or Expense Bank in Branch")
		
	# def make_pol_entry(self):
	# 	if getdate(self.posting_date) <= getdate("2024-03-31"):
	# 					return
	# 	container = frappe.db.get_value("Equipment Type", frappe.db.get_value("Equipment", self.equipment, "equipment_type"), "is_container")
	# 	if self.equipment_branch == self.fuelbook_branch:
	# 		own = 1
	# 	else:
	# 		own = 0

	# 	con = frappe.new_doc("POL Entry")
	# 	con.flags.ignore_permissions = 1	
	# 	con.equipment = self.equipment
	# 	con.pol_type = self.pol_type
	# 	con.branch = self.equipment_branch
	# 	con.posting_date = self.posting_date
	# 	con.posting_time = self.posting_time
	# 	con.qty = self.qty
	# 	con.reference_type = "POL Receive"
	# 	con.reference_name = self.name
	# 	con.is_opening = 0
	# 	con.own_cost_center = own
	# 	if container:
	# 		con.type = "Stock"
	# 		con.submit()
		
	# 	if self.direct_consumption:
	# 		con1 = frappe.new_doc("POL Entry")
	# 		con1.flags.ignore_permissions = 1	
	# 		con1.equipment = self.equipment
	# 		con1.pol_type = self.pol_type
	# 		con1.branch = self.equipment_branch
	# 		con1.posting_date = self.posting_date
	# 		con1.posting_time = self.posting_time
	# 		con1.qty = self.qty
	# 		con1.reference_type = "POL Receive"
	# 		con1.reference_name = self.name
	# 		con1.type = "Receive"
	# 		con1.is_opening = 0
	# 		con1.own_cost_center = own
	# 		con1.submit()
	# 	else:
	# 		con1 = frappe.new_doc("POL Entry")
	# 		con1.flags.ignore_permissions = 1	
	# 		con1.equipment = self.tanker
	# 		con1.pol_type = self.pol_type
	# 		con1.branch = self.tanker_branch
	# 		con1.posting_date = self.posting_date
	# 		con1.posting_time = self.posting_time
	# 		con1.qty = self.qty
	# 		con1.reference_type = "POL Receive"
	# 		con1.reference_name = self.name
	# 		# con1.type = "Receive"
	# 		if container:
	# 			con1.type = "Stock"
	# 		con1.is_opening = 0
	# 		con1.own_cost_center = own
	# 		con1.submit()	
			
	# 		if container:
	# 			con2 = frappe.new_doc("POL Entry")
	# 			con2.flags.ignore_permissions = 1	
	# 			con2.equipment = self.equipment
	# 			con2.pol_type = self.pol_type
	# 			con2.branch = self.equipment_branch
	# 			con2.posting_date = self.posting_date
	# 			con2.posting_time = self.posting_time
	# 			con2.qty = self.qty
	# 			con2.reference_type = "POL Receive"
	# 			con2.reference_name = self.name
	# 			con2.type = "Issue"
	# 			con2.is_opening = 0
	# 			con2.own_cost_center = own
	# 			con2.submit()
	# 		# else:
	# 		# 	con2 = frappe.new_doc("POL Entry")
	# 		# 	con2.flags.ignore_permissions = 1	
	# 		# 	con2.equipment = self.equipment
	# 		# 	con2.pol_type = self.pol_type
	# 		# 	con2.branch = self.equipment_branch
	# 		# 	con2.posting_date = self.posting_date
	# 		# 	con2.posting_time = self.posting_time
	# 		# 	con2.quantity = self.qty
	# 		# 	con2.reference_type = "POL Receive"
	# 		# 	con2.reference_name = self.name
	# 		# 	con2.type = "Issue"
	# 		# 	con2.is_opening = 0
	# 		# 	con2.own_cost_center = own
	# 		# 	con2.submit()
	#
	# 
	# 
	# 
	def make_pol_entry(self):
		if getdate(self.posting_date) <= getdate("2018-03-31"):
						return
		container = frappe.db.get_value("Equipment Type", frappe.db.get_value("Equipment", self.equipment, "equipment_type"), "is_container")
		if self.equipment_branch == self.fuelbook_branch:
			own = 1
		else:
			own = 0

		con = frappe.new_doc("POL Entry")
		con.flags.ignore_permissions = 1	
		con.equipment = self.equipment
		con.pol_type = self.pol_type
		con.branch = self.equipment_branch
		con.posting_date = self.posting_date
		con.posting_time = self.posting_time
		con.qty = self.qty
		con.reference_type = "POL Receive"
		con.reference_name = self.name
		con.is_opening = 0
		con.own_cost_center = own
		if container:
			con.type = "Stock"
			con.submit()
		
		if self.direct_consumption:
			con1 = frappe.new_doc("POL Entry")
			con1.flags.ignore_permissions = 1	
			con1.equipment = self.equipment
			con1.pol_type = self.pol_type
			con1.branch = self.equipment_branch
			con1.posting_date = self.posting_date
			con1.posting_time = self.posting_time
			con1.qty = self.qty
			con1.reference_type = "POL Receive"
			con1.reference_name = self.name
			con1.type = "Receive"
			con1.is_opening = 0
			con1.own_cost_center = own
			con1.submit()
			
			if container:
				con2 = frappe.new_doc("POL Entry")
				con2.flags.ignore_permissions = 1	
				con2.equipment = self.equipment
				con2.pol_type = self.pol_type
				con2.branch = self.equipment_branch
				con2.posting_date = self.posting_date
				con2.posting_time = self.posting_time
				con2.qty = self.qty
				con2.reference_type = "POL Receive"
				con2.reference_name = self.name
				con2.type = "Issue"
				con2.is_opening = 0
				con2.own_cost_center = own
				con2.submit()	


	def delete_pol_entry(self):
		frappe.db.sql("delete from `tabPOL Entry` where reference_name = %s", self.name)						

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
def get_equipment_data(equipment_name, all_equipment=0, branch=None):
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
    if equipment_name:
        query += " AND e.name = %(equipment_name)s"
    
    query += " ORDER BY e.branch"
    
    items = frappe.db.sql("""
        SELECT item_code, item_name, stock_uom 
        FROM `tabItem`
        WHERE is_hsd_item = 1 AND disabled = 0
    """, as_dict=True)
    
    equipment_details = frappe.db.sql(query, {
        'branch': branch,
        'equipment_name': equipment_name
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

			# if received or issued:
			# 		row = [received, issued, flt(received) - flt(issued)]
			# 		data.append(row)	
    
    return data

# @frappe.whitelist()
# def get_equipment_data(equipment_name, all_equipment=0, branch=None, book_type=None):
#     data = []
    
#     query = """
#         SELECT e.name, e.branch, e.registration_number, e.hsd_type, e.equipment_type
#         FROM `tabEquipment` e
#         JOIN `tabEquipment Type` et ON e.equipment_type = et.name
#     """

#     if not all_equipment:
#         query += " WHERE et.is_container = 1"
#     else:
#         query += " WHERE 1=1"
    
#     if branch:
#         query += " AND e.branch = %(branch)s"
#     if equipment_name:
#         query += " AND e.name = %(equipment_name)s"
    
#     query += " ORDER BY e.branch"
    
#     items = frappe.db.sql("""
#         SELECT item_code, item_name, stock_uom 
#         FROM `tabItem`
#         WHERE is_hsd_item = 1 AND disabled = 0
#     """, as_dict=True)
    
#     equipment_details = frappe.db.sql(query, {
#         'branch': branch,
#         'equipment_name': equipment_name
#     }, as_dict=True)
    
#     for eq in equipment_details:
#         for item in items:
#             received = issued = 0
#             if book_type == "Common":
#                 received = get_pol_tills("Stock", eq.name, item.item_code)
#                 issued = get_pol_tills("Issue", eq.name, item.item_code)
#             elif book_type == "Own": 
#                 received = get_pol_till("Receive", eq.name, item.item_code)
#                 issued = get_pol_consumed_tills(eq.name)

#             if received or issued:
#                 data.append({
#                     'received': received,
#                     'issued': issued,
#                     'balance': flt(received) - flt(issued)
#                 })

#     return data




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


# @frappe.whitelist()
# def get_equipment_datas(equipment_name, all_equipment=0, branch=None):
#     data = []
    
#     query = """
#         SELECT e.name, e.branch, e.registration_number, e.hsd_type, e.equipment_type
#         FROM `tabEquipment` e
#         JOIN `tabEquipment Type` et ON e.equipment_type = et.name
#     """

#     if not all_equipment:
#         query += " WHERE et.is_container = 1"
#     else:
#         query += " WHERE 1=1"
    
#     if branch:
#         query += " AND e.branch = %(branch)s"
#     if equipment_name:
#         query += " AND e.name = %(equipment_name)s"
    
#     query += " ORDER BY e.branch"
    
#     items = frappe.db.sql("""
#         SELECT item_code, item_name, stock_uom 
#         FROM `tabItem`
#         WHERE is_hsd_item = 1 AND disabled = 0
#     """, as_dict=True)
    
#     equipment_details = frappe.db.sql(query, {
#         'branch': branch,
#         'equipment_name': equipment_name
#     }, as_dict=True)
    
#     for eq in equipment_details:
#         for item in items:
#             received = issued = 0
#             if all_equipment:
#                 if eq.hsd_type == item.item_code:
#                     received = get_pol_till_tanker("Receive", eq.name, item.item_code)
#                     issued = get_pol_consumed_till_tanker(eq.name,)
#             else:
#                 received = get_pol_till_tanker("Stock", eq.name, item.item_code)
#                 issued = get_pol_consumed_till_tanker("Issue", eq.name, item.item_code)
						
            
#             if received or issued:
#                 data.append({
#                     'received': received,
#                     'issued': issued,
#                     'balance': flt(received) - flt(issued)
#                 })

# 			# if received or issued:
# 			# 		row = [received, issued, flt(received) - flt(issued)]
# 			# 		data.append(row)	
    
#     return data

@frappe.whitelist()
def get_tanker_data(doctype, txt, searchfield, start, page_len, filters):
	
    if not filters.get('branch'):
        frappe.throw(_("Branch is required to fetch the equipment."))

    # frappe.throw("jjjjjj")
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

# @frappe.whitelist()
# def get_tanker_details(tanker, posting_date, pol_type):
#     received_till = get_pol_till_tanker("Stock", tanker, posting_date, pol_type)
#     issue_till = get_pol_till_tanker("Issue", tanker, posting_date, pol_type)
#     balance = flt(received_till) - flt(issue_till)
#     return {"balance": balance}


# @frappe.whitelist()
# def tanker_balance(pol_receive):
# 	t, m = frappe.db.get_value("POL Receive", pol_receive, ['tanker_type', 'tanker_number'])
# 	data = frappe.db.sql("select qty from `tabPOL Receive` where tanker_type = %s and tanker_number = %s", (t, m), as_dict=True)
# 	if not data:
# 		frappe.throw("Setup yardstick for " + str(m))
# 	return data


# Tanker Balance
@frappe.whitelist()
def get_balance_details(book_type, tanker=None, equipment=None, posting_date=None, pol_type=None):
    """
    Fetch the balance details for tanker or equipment based on the book_type.
    """
    if not posting_date:
        frappe.throw("Posting Date is mandatory.")

    if book_type == "Common" and equipment:
        # Fetch tanker balances
        received_till = get_pol_till("Stock", equipment, posting_date, pol_type)
        issue_till = get_pol_till("Issue", equipment, posting_date, pol_type)
        tanker_balance = flt(received_till) - flt(issue_till)
        return {"tanker_balance": tanker_balance, "tank_balance": 0}

    elif book_type == "Own" and equipment:
        # Fetch equipment balances
        received_till = get_pol_till("Stock", equipment, posting_date, pol_type)
        issue_till = get_pol_till("Issue", equipment, posting_date, pol_type)
        tank_balance = flt(received_till) - flt(issue_till)
        return {"tanker_balance": 0, "tank_balance": tank_balance}

    else:
        frappe.throw("Invalid inputs. Please ensure the correct book_type, tanker, or equipment is provided.")
