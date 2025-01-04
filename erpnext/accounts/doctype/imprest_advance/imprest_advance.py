# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt, cint, nowdate, getdate, formatdate, money_in_words
# from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states

class ImprestAdvance(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		abstract_bill: DF.Data | None
		adjusted_amount: DF.Currency
		advance_amount: DF.Currency
		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Link | None
		approver_name: DF.Data | None
		balance_amount: DF.Currency
		branch: DF.Link
		business_activity: DF.Link
		company: DF.Link | None
		cost_center: DF.Link
		imprest_recoup: DF.Link | None
		imprest_type: DF.Link
		is_opening: DF.Check
		journal_entry: DF.Data | None
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
		# self.calculate_adjusted_amount()

	def before_cancel(self):
		if self.abstract_bill:
			ab_status = frappe.get_value("Abstract Bill", {"name": self.abstract_bill}, "docstatus")
			if cint(ab_status) == 1:
				frappe.throw("Abstract Bill {} for this transaction needs to be cancelled first".format(frappe.get_desk_link("Abstract Bill", self.abstract_bill)))
			else:
				frappe.db.sql("delete from `tabAbstract Bill` where name = '{}'".format(self.abstract_bill))
				self.db_set("abstract_bill", None)

	def validate_advance_amount(self):
		imprest_limit = self.get_imprest_limit()
		balance_amount = self.get_balance_amount()

		message = "Advance amount requested cannot be greater than Imprest Limit <b>{}</b> for imprest type <b>{}</b>".format(imprest_limit, self.imprest_type)

		bal_amt = 0
		if balance_amount:
			bal_amt =  flt(imprest_limit) - flt(balance_amount)
			if bal_amt == 0:
				frappe.throw("Your imprest advance in already reached at limit {}".format(frappe.bold(imprest_limit)))
			elif bal_amt < flt(imprest_limit):
				self.advance_amount = bal_amt
				self.balance_amount = bal_amt
		else:
			if flt(self.advance_amount) > flt(imprest_limit):
				frappe.throw(message)
	
	def get_balance_amount(self):
		query = """
				SELECT ia.balance_amount 
				FROM `tabImprest Advance` ia
				WHERE ia.party_type=%s
				AND ia.party=%s
				AND ia.imprest_type=%s 
				AND ia.docstatus = 1
				"""
		data = frappe.db.sql(query, (self.party_type, self.party, self.imprest_type), as_dict=True)
		total_bal_amt = 0
		for d in data:
			total_bal_amt += d.balance_amount
		return total_bal_amt

	@frappe.whitelist()
	def set_advance_amount(self):
		if not self.imprest_type:
			frappe.throw("Please set <strong>Imprest Type</strong>.")
		balance_amount = self.get_balance_amount()
		imprest_limit = frappe.db.get_value("Imprest Type",  self.imprest_type, "imprest_max_limit")
		if not imprest_limit:
			frappe.throw("Please set Imprest Limit in {}".format(
				frappe.get_desk_link("Imprest Type", self.imprest_type)
			))
		if balance_amount == imprest_limit:
			frappe.throw("Your imprest advance in already reached at limit {}".format(frappe.bold(imprest_limit)))
		if balance_amount:
			return flt(imprest_limit) - flt(balance_amount)
		else:
			return imprest_limit

	def calculate_adjusted_amount(self):
		if self.is_opening:
			return

		if self.od_items:
			tot_od_amt = sum(d.od_amount for d in self.od_items)
			self.adjusted_amount = flt(tot_od_amt)  
			self.balance_amount = flt(self.advance_amount) - flt(tot_od_amt)  

	def get_imprest_limit(self):
		imprest_limit = frappe.db.get_value("Imprest Type",  self.imprest_type, "imprest_max_limit")
		if not imprest_limit:
			frappe.throw("Please set Imprest Limit in {}".format(
				frappe.get_desk_link("Imprest Type", self.imprest_type)
			))

		return imprest_limit

	def on_submit(self):
		if not self.is_opening:
			self.create_abstract_bill()

	def on_cancel(self):
		# if self.imprest_recoup:
		# 	frappe.throw("Imprest Recoup <b>{}</b> needs to to cancelled first.".format(self.imprest_recoup))
		pass

	def get_imprest_type_account(self, imprest_type):
		account = frappe.db.get_value(
			"Imprest Type Account",
			{"parent": imprest_type, "company": self.company},
			"account",
			cache=True,
		)

		if not account:
			frappe.throw(
				_("Please set account in Imprest Type {0}").format(
					frappe.get_desk_link("Imprest Type", imprest_type)
				)
			)

		return account
			
	def create_abstract_bill(self):
		imprest_advance_account = self.get_imprest_type_account(self.imprest_type)
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
		frappe.msgprint(_('Abstarct Bill {0} posted').format(frappe.get_desk_link("Abstract Bill", ab.name)))

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	# if user == "Administrator" or "System Manager" in user_roles or "Accounts User" in user_roles or "Account Manager" in user_roles: 
	if any(role in user_roles for role in {"Administrator", "System Manager", "Accounts User", "Account Manager"}):
		return

	return """(
		`tabImprest Recoup`.owner = '{user}'
		or
		exists(select 1
			from `tabEmployee` as e
			where e.branch = `tabImprest Recoup`.branch
			and e.user_id = '{user}')
		or
		exists(select 1
			from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
			where e.user_id = '{user}'
			and ab.employee = e.name
			and bi.parent = ab.name
			and bi.branch = `tabImprest Recoup`.branch)
	)""".format(user=user)
