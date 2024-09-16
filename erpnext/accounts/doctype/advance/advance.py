# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, cint, nowdate, getdate, formatdate, money_in_words
from frappe.model.document import Document

class Advance(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		abstract_bill: DF.Data | None
		adjusted_amount: DF.Currency
		advance_amount: DF.Currency
		advance_recoup: DF.Link | None
		advance_type: DF.Link
		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Link | None
		approver_name: DF.Data | None
		balance_amount: DF.Currency
		branch: DF.Link
		business_activity: DF.Link
		company: DF.Link | None
		cost_center: DF.Link
		is_opening: DF.Check
		opening_amount: DF.Currency
		party: DF.DynamicLink
		party_type: DF.Literal["", "Employee", "Agency"]
		posting_date: DF.Date
		remarks: DF.SmallText | None
		title: DF.Data
	# end: auto-generated types
	
	def validate(self):
		if not self.is_opening:
			self.validate_advance_amount()

	def on_submit(self):
		if not self.is_opening:
			self.create_abstract_bill()

	def validate_advance_amount(self):
		imprest_limit = self.get_max_limit()
		balance_amount = self.get_balance_amount()

		message = "Advance amount requested cannot be greater than max Limit <b>{}</b> for advance type <b>{}</b>".format(imprest_limit, self.advance_type)

		bal_amt = 0
		if balance_amount:
			bal_amt =  flt(imprest_limit) - flt(balance_amount)
			if bal_amt == 0:
				frappe.throw("Your advance in already reached at limit {}".format(frappe.bold(imprest_limit)))
			elif bal_amt < flt(imprest_limit):
				self.advance_amount = bal_amt
				self.balance_amount = bal_amt
		else:
			if flt(self.advance_amount) > flt(imprest_limit):
				frappe.throw(message)

	def get_max_limit(self):
		imprest_limit = frappe.db.get_value("Advance Type",  self.advance_type, "max_limit")
		if not imprest_limit:
			frappe.throw("Please set Advance Limit in {}".format(
				frappe.get_desk_link("Advance Type", self.advance_type)
			))

		return imprest_limit

	def get_balance_amount(self):
		query = """
				SELECT a.balance_amount 
				FROM `tabAdvance` a
				WHERE a.party_type=%s
				AND a.party=%s
				AND a.advance_type=%s 
				AND a.docstatus = 1
				"""
		data = frappe.db.sql(query, (self.party_type, self.party, self.advance_type), as_dict=True)
		total_bal_amt = 0
		for d in data:
			total_bal_amt += d.balance_amount
		return total_bal_amt

	@frappe.whitelist()
	def set_advance_amount(self):
		if not self.advance_type:
			frappe.throw("Please set <strong>Advance Type</strong>.")
		balance_amount = self.get_balance_amount()
		max_limit = frappe.db.get_value("Advance Type",  self.advance_type, "max_limit")
		if not max_limit:
			frappe.throw("Please set Advance Max Limit in {}".format(
				frappe.get_desk_link("Advance Type", self.advance_type)
			))
		if balance_amount == max_limit:
			frappe.throw("Your advance in already reached at limit {}".format(frappe.bold(max_limit)))
		if balance_amount:
			return flt(max_limit) - flt(balance_amount)
		else:
			return max_limit
		
	def get_advance_type_account(self, advance_type):
		account = frappe.db.get_value(
			"Advance Type Account",
			{"parent": advance_type, "company": self.company},
			"account",
			cache=True,
		)

		if not account:
			frappe.throw(
				_("Please set account in Advance Type {0}").format(
					frappe.get_desk_link("Advance Type", advance_type)
				)
			)

		return account
		
	def create_abstract_bill(self):
		imprest_advance_account = self.get_advance_type_account(self.advance_type)
		items = []
		items.append({
			"account": imprest_advance_account,
			"cost_center": self.cost_center,
			"party_type": self.party_type,
			"party": self.party,
			"business_activity": self.business_activity,
			"amount": self.advance_amount,
		})		
		ab = frappe.new_doc("Abstract Bill")
		ab.flags.ignore_permission = 1
		ab.update({
			"doctype": "Abstract Bill",
			"posting_date": self.posting_date,
			"company": self.company,
			"branch": self.branch,
			"reference_doctype": self.doctype,
			"reference_name": self.name,
			"items": items,
		})
		ab.insert()
		self.db_set('abstract_bill', ab.name)
		frappe.msgprint(_('Abstarct Bill {0} posted from Advance').format(frappe.get_desk_link("Abstract Bill", ab.name)))
