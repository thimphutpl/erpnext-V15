# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.accounts.doctype.business_activity.business_activity import get_default_ba
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.custom_utils import check_budget_available
import json
from frappe import _, msgprint
from frappe.utils import flt, cint, nowdate, getdate, formatdate, money_in_words


class POLAdvance(AccountsController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.pol_od_item.pol_od_item import POLODitem
		from frappe.types import DF

		adjusted_amount: DF.Currency
		amended_from: DF.Link | None
		amount: DF.Currency
		approved_by: DF.Data | None
		balance_amount: DF.Currency
		branch: DF.Link
		business_activity: DF.Link
		cheque_date: DF.Date | None
		cheque_no: DF.Data | None
		clearance_date: DF.Date | None
		company: DF.Link
		cost_center: DF.Link | None
		currency: DF.Link
		entry_date: DF.Date
		equipment: DF.Link
		equipment_number: DF.Data | None
		expense_account: DF.Link
		fuelbook: DF.Link | None
		fuelbook_branch: DF.Link | None
		is_opening: DF.Check
		items: DF.Table[POLODitem]
		je_status: DF.Literal["", "Submitted"]
		journal_entry: DF.Data | None
		od_adjusted_amount: DF.Currency
		od_amount: DF.Currency
		od_outstanding_amount: DF.Currency
		party_type: DF.Literal["Supplier"]
		pay_to_recd_from: DF.Data | None
		payment_type: DF.Data | None
		select_cheque_lot: DF.Link | None
		supplier: DF.Link
		use_check_lot: DF.Check
		user_remark: DF.SmallText | None
		workflow_state: DF.Link | None
	# end: auto-generated types
	def validate(self):
		self.validate_cheque_info()
		self.od_adjustment()
		if self.is_opening and flt(self.od_amount) > flt(0.0):
			self.od_outstanding_amount = flt(self.od_amount)
		else:
			self.od_amount = self.od_outstanding_amount = 0.0

	def before_cancel(self):
		if self.is_opening:
			return
		if self.journal_entry:
			for t in frappe.get_all("Journal Entry", ["name"], {"name": self.journal_entry, "docstatus": ("<",2)}):
				frappe.throw(_('Journal Entry {} for this transaction needs to be cancelled first').format(frappe.get_desk_link(self.doctype,self.journal_entry)),title='Not permitted')

	def on_submit(self):
		if not self.is_opening:
			# check_budget_available(self.cost_center,advance_account,self.entry_date,self.amount,self.business_activity)
			self.update_od_balance()
			# self.post_journal_entry()
			abstract_bill = frappe.db.sql('''
                                 select abstract_bill_required from `tabCompany` where name='{name}' limit 1
                                 '''.format(name=self.company))
			# frappe.throw(str(abstract_bill[0][0]))
			if abstract_bill and abstract_bill[0][0] == 1:
				self.create_abstract_bill()
			else:
				self.post_journal_entry()

	def on_cancel(self):
		if not self.is_opening:
			# self.cancel_budget_entry()
			self.update_od_balance()

	def update_od_balance(self):
		if self.is_opening:
			return
		for d in self.items:
			doc = frappe.get_doc('POL Advance',d.reference)
			if self.docstatus == 2:
				if flt(self.adjusted_amount) - flt(doc.od_amount) < 0:
					self.adjusted_amount = 0
					self.balance_amount = flt(self.amount)
				else:
					self.adjusted_amount = flt(self.adjusted_amount) - flt(doc.od_amount)
					self.balance_amount = flt(self.balance_amount) + flt(doc.od_amount)
				self.od_amount = 0
				self.od_outstanding_amount = 0
				doc.od_adjusted_amount = 0 
				doc.od_outstanding_amount = doc.od_amount
				doc.save(ignore_permissions=True)
			elif self.docstatus == 1:
				if flt(self.adjusted_amount) == flt(self.amount):
					self.od_amount += doc.od_amount
					self.od_outstanding_amount += doc.od_amount
				elif flt(self.adjusted_amount) + flt(doc.od_amount) > flt(self.amount):
					excess_amount = flt(self.adjusted_amount) + flt(doc.od_amount) - flt(self.amount)
					self.od_amount += flt(excess_amount)
					self.od_outstanding_amount += flt(excess_amount)
					if self.adjusted_amount != self.amount:
						self.adjusted_amount = flt(self.amount)
						self.balance_amount = flt(self.amount) - flt(self.adjusted_amount)
				else:
					self.adjusted_amount += flt(doc.od_amount)
					self.balance_amount = flt(self.amount) - flt(self.adjusted_amount)
				doc.od_adjusted_amount = doc.od_outstanding_amount 
				doc.od_outstanding_amount = 0
				doc.save(ignore_permissions=True)
				self.save()

	def od_adjustment(self):
		data = frappe.db.sql('''
			SELECT
				name as reference, od_amount,
				od_outstanding_amount
			FROM `tabPOL Advance`
			WHERE od_outstanding_amount > 0
			and docstatus = 1
			and equipment = '{}'
		'''.format(self.equipment),as_dict=True)
		
		if data :
			self.set('items',[])
			for d in data:
				row = self.append('items',{})
				row.update(d)

	def validate_cheque_info(self):
		if self.cheque_date and not self.cheque_no:
			frappe.msgprint(_("Cheque No is mandatory if you entered Cheque Date"), raise_exception=1)
  
	# def cancel_budget_entry(self):
	# 	frappe.db.sql("delete from `tabConsumed Budget` where reference_no = %s", self.name) 
   
	def post_journal_entry(self):
		if not self.amount:
			frappe.throw(_("Amount should be greater than zero"))
		if self.is_opening:
			return

		self.posting_date = self.entry_date
		ba = self.business_activity

		credit_account = self.expense_account
		advance_account = frappe.db.get_value("Company", self.company, "pol_advance_account")
			
		if not credit_account:
			frappe.throw("Expense Account is mandatory")
		if not advance_account:
			frappe.throw("Setup POL Advance Account in Maintenance Accounts Settings")

		account_type = frappe.db.get_value("Account", credit_account, "account_type")
		voucher_type = "Journal Entry"
		voucher_series = "Journal Voucher"
		party_type = ''
		party = ''
		if account_type == "Bank":
			voucher_type = "Bank Entry"
			voucher_series = "Bank Receipt Voucher" if self.payment_type == "Receive" else "Bank Payment Voucher"
		elif account_type == "Payable":
			party_type = self.party_type
			party = self.supplier

		r = []
		if self.cheque_no:
			if self.cheque_date:
				r.append(_('Reference #{0} dated {1}').format(self.cheque_no, formatdate(self.cheque_date)))
			else:
				frappe.msgprint(_("Please enter Cheque Date date"), raise_exception=frappe.MandatoryError)
		if self.user_remark:
			r.append(_("Note: {0}").format(self.user_remark))

		remarks = ("").join(r)

		je = frappe.new_doc("Journal Entry")

		je.update({
			"doctype": "Journal Entry",
			"voucher_type": voucher_type,
			"naming_series": voucher_series,
			"title": "POL Advance - " + self.equipment,
			"user_remark": remarks if remarks else "Note: " + "POL Advance - " + self.equipment,
			"posting_date": self.posting_date,
			"company": self.company,
			"total_amount_in_words": money_in_words(self.amount),
			"branch": self.fuelbook_branch,
		})

		je.append("accounts",{
			"account": advance_account,
			"debit_in_account_currency": self.amount,
			"cost_center": self.cost_center,
			"party_check": 1,
			"party_type": self.party_type,
			"party": self.supplier,
			"business_activity": ba
		})

		je.append("accounts",{
			"account": credit_account,
			"credit_in_account_currency": self.amount,
			"cost_center": self.cost_center,
			"reference_type": "POL Advance",
			"reference_name": self.name,
			"party_type": party_type,
			"party": party,
			"business_activity": ba
		})

		je.insert()

		self.db_set("journal_entry",je.name)
		frappe.msgprint(_('Journal Entry {} posted to accounts').format(frappe.get_desk_link(je.doctype,je.name)))


	def create_abstract_bill(self):
     
		data = frappe.db.sql("""
		select pol_advance_account from `tabCompany` where name='Office of the Gyalpoi Zimpon'
		""", as_dict=True)

		# Accessing the result
		if data:
			pol_advance_account = data[0].get('pol_advance_account')
		else:
			frappe.throw("Add pol_advance_account in company")
		

		# imprest_advance_account = self.get_imprest_type_account(self.imprest_type)
		items = []
		items.append({
			"account": pol_advance_account,
			"cost_center": self.cost_center,
			"party_type": self.party_type,
			"party": self.supplier,
			"business_activity": self.business_activity,
			"amount": self.amount,
		})		
		ab = frappe.new_doc("Abstract Bill")
		ab.flags.ignore_permission = 1
		ab.update({
			"doctype": "Abstract Bill",
			"posting_date": self.entry_date,
			"company": self.company,
			"branch": self.branch,
			"reference_doctype": self.doctype,
			"reference_name": self.name,
			"items": items,
		})
		ab.insert()
		frappe.msgprint(_('Abstarct Bill {0} posted to accounts').format(frappe.get_desk_link("Abstract Bill", ab.name)))

