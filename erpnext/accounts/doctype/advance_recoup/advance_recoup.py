# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint, nowdate, getdate, formatdate, money_in_words

class AdvanceRecoup(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.advance_detail.advance_detail import AdvanceDetail
		from erpnext.accounts.doctype.advance_recoup_item.advance_recoup_item import AdvanceRecoupItem
		from erpnext.accounts.doctype.transaction_selection.transaction_selection import TransactionSelection
		from frappe.types import DF

		abstract_bill: DF.Data | None
		advance_type: DF.Link
		advances: DF.Table[AdvanceDetail]
		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Link | None
		approver_name: DF.Data | None
		balance_amount: DF.Currency
		branch: DF.Link
		business_activity: DF.Link
		company: DF.Link
		cost_center: DF.Link
		excess_amount: DF.Currency
		fetch_from_other_transactions: DF.Check
		final_je: DF.Data | None
		final_settlement: DF.Literal["", "Yes", "No"]
		items: DF.Table[AdvanceRecoupItem]
		journal_entry: DF.Data | None
		opening_balance: DF.Currency
		party: DF.DynamicLink
		party_type: DF.Literal["", "Employee", "Agency"]
		posting_date: DF.Date
		remarks: DF.SmallText | None
		select_transactions: DF.TableMultiSelect[TransactionSelection]
		title: DF.Data
		total_allocated_amount: DF.Currency
		total_amount: DF.Currency
	# end: auto-generated types
	
	def validate(self):
		self.calculate_amount()
		self.populate_advances()
		self.calculate_amount_final()

	def on_submit(self):
		self.update_reference_document()
		if self.final_settlement == "Yes":
			self.create_abstract_bill()
		else:
			self.create_abstract_bill()
			self.create_auto_advance()	

	def before_cancel(self):
		if self.abstract_bill:
			ab_status = frappe.get_value("Abstract Bill", {"name": self.abstract_bill}, "docstatus")
			if cint(ab_status) == 1:
				frappe.throw("Abstract Bill {} for this transaction needs to be cancelled first".format(frappe.get_desk_link("Abstract Bill", self.abstract_bill)))
			else:
				frappe.db.sql("delete from `tabAbstract Bill` where name = '{}'".format(self.abstract_bill))
				self.db_set("abstract_bill", None)

		self.check_imprest_advance_status_and_cancel()

	def on_cancel(self):
		self.update_reference_document(cancel=True)
		self.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry")

	def calculate_amount(self):
		total_payable_amt = sum(d.amount for d in self.items) if self.items else 0
		self.total_amount = total_payable_amt

	def calculate_amount_final(self):
		tot_adv_amt = sum(d.advance_amount for d in self.advances)
		tot_bal_amt = sum(d.balance_amount for d in self.advances)
		tot_allocated_amt = sum(d.allocated_amount for d in self.advances)
		self.opening_balance = flt(tot_adv_amt)
		self.balance_amount = flt(tot_bal_amt)
		self.total_allocated_amount = flt(tot_allocated_amt)
		if flt(self.total_amount) > flt(tot_allocated_amt):
			self.excess_amount = flt(self.total_amount) - flt(tot_allocated_amt)
		else:
			self.excess_amount = 0

	def update_reference_document(self, cancel=False):
		for d in self.advances:
			doc = frappe.get_doc("Advance", d.advance)
			allocated_amount = flt(d.allocated_amount)
			if cancel:
				doc.balance_amount += allocated_amount
				doc.adjusted_amount -= allocated_amount
			else:
				doc.balance_amount -= allocated_amount
				doc.adjusted_amount += allocated_amount
			doc.save(ignore_permissions=True)

	def create_abstract_bill(self):
		bank_account = frappe.db.get_value("Company", self.company, "default_bank_account")
		if not bank_account:
			frappe.throw("Set Default Bank Account in Company {}".format(frappe.get_desk_link(self.company)))
		items = []
		for item in self.get("items"):
			items.append({
				"account": item.account,
				"cost_center": item.cost_center,
				"party_type": self.party_type,
				"party": self.party,
				"business_activity": item.business_activity,
				"amount": item.amount,
				"cash_receipt": self.balance_amount if self.final_settlement == "Yes" else 0,
				"reimburse_amount": self.excess_amount if self.final_settlement == "Yes" else 0
			})
		if self.balance_amount and self.final_settlement == "Yes":
			items.append({
				"account": bank_account,
				"cost_center": self.cost_center,
				"party_type": self.party_type,
				"party": self.party,
				"business_activity": self.business_activity,
				"amount": self.balance_amount,
				"not_required": 1,
			})
		ab = frappe.new_doc("Abstract Bill")
		ab.flags.ignore_permission = 1
		ab.update({
			"doctype": "Abstract Bill",
			"posting_date": self.posting_date,
			"branch": self.branch,
			"company": self.company,
			"reference_doctype": self.doctype,
			"reference_name": self.name,
			"items": items,
			"final_settlement": 1 if self.final_settlement == "Yes" else 0
		})
		ab.insert()
		self.db_set('abstract_bill', ab.name)
		frappe.msgprint(_('Abstract Bill {0} created from Advance Recoup').format(frappe.get_desk_link("Abstract Bill", ab.name)))

	def create_auto_advance(self):
		imprest_limit = frappe.db.get_value("Advance Type",  self.advance_type, "max_limit")
		if not imprest_limit:
			frappe.throw("Please set Advance Max Limit in {}".format(
				frappe.get_desk_link("Advance Type", self.advance_type)
			))

		bal_amt = flt(imprest_limit) - flt(self.total_allocated_amount)
		if bal_amt > 0:
			advance_amount = flt(bal_amt)
		else:
			advance_amount = flt(imprest_limit)
			
		if self.total_amount:
			ima = frappe.new_doc("Advance")
			ima.update({
				"company": self.company,
				"branch": self.branch,
				"posting_date": self.posting_date,
				"title": f"Auto Imprest Allocation from - {self.name}",
				"remarks": f"Note: Auto created Advance Allocation from Recoup - {self.name}",
				"advance_type": self.advance_type,
				"party_type": self.party_type,
				"party": self.party,
				"advance_amount": advance_amount,
				"balance_amount": advance_amount,
				"business_activity": self.business_activity,
				"advance_recoup": self.name,
			})
			ima.insert()
			ima.submit()
			frappe.msgprint("Advance created {}".format(frappe.get_desk_link("Advance", ima.name)))

	def check_imprest_advance_status_and_cancel(self):
		ima = frappe.db.sql("select name from `tabAdvance` where advance_recoup = '{}' and docstatus = 1".format(self.name))
		if ima:
			ia_doc = frappe.get_doc("Advance", {"name": ima})
			ia_doc.cancel()

	@frappe.whitelist()
	def populate_advances(self):
		if not self.advance_type or not self.party or not self.branch:
			frappe.throw("Please insert the mandatory fields")
		else:
			self.set('advances', [])
			query = """
				SELECT 
					a.name, a.opening_amount, a.advance_amount, a.balance_amount, a.is_opening
				FROM `tabAdvance` a
				WHERE a.docstatus = 1 
					AND a.posting_date <= '{date}'
					AND a.balance_amount > 0
					AND a.advance_type = '{advance_type}'
					AND a.party = '{party}'
				ORDER BY a.posting_date
			""".format(date=self.posting_date, advance_type=self.advance_type, party=self.party)

			data = frappe.db.sql(query, as_dict=True)

			if not data:
				frappe.throw("No Advance")

			allocated_amount = self.total_amount or 0
			total_amount_adjusted = 0

			for d in data:
				row = self.append('advances', {
					'advance': d.name,
					'advance_amount': d.balance_amount,
				})

				if d.balance_amount >= allocated_amount:
					row.allocated_amount = allocated_amount
					row.balance_amount = d.balance_amount - allocated_amount
					allocated_amount = 0
				else:
					row.allocated_amount = d.balance_amount
					row.balance_amount = 0
					allocated_amount -= d.balance_amount

			if not self.advances:
				frappe.throw("No Advance")