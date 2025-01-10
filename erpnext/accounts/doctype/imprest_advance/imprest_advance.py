# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt, cint, nowdate, getdate, formatdate, money_in_words
from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states

class ImprestAdvance(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		adjusted_amount: DF.Currency
		amended_from: DF.Link | None
		amount: DF.Currency
		approver: DF.Link | None
		approver_designation: DF.Link | None
		approver_name: DF.Data | None
		balance_amount: DF.Currency
		branch: DF.Link
		company: DF.Link | None
		cost_center: DF.Link
		first_advance: DF.Check
		imprest_recoup: DF.Link | None
		imprest_type: DF.Link
		is_opening: DF.Check
		journal_entry: DF.Data | None
		party: DF.DynamicLink
		party_type: DF.Literal["", "Employee"]
		posting_date: DF.Date
		project: DF.Link | None
		remarks: DF.SmallText | None
		title: DF.Data
	# end: auto-generated types

	def validate(self):
		if not self.is_opening:
			self.check_imprest_amount()
		if cint(self.first_advance) == 1:
			self.check_for_duplicate_entry()
			validate_workflow_states(self)
			if self.workflow_state != "Approved":
				notify_workflow_states(self)

	def check_for_duplicate_entry(self):
		import datetime

		date_obj = datetime.datetime.strptime(str(self.posting_date), "%Y-%m-%d")
		year = date_obj.year

		filters = {
			"branch": self.branch,
			"imprest_type": self.imprest_type,
			"docstatus": 1,
			"party": self.party
		}

		if self.project:
			filters["project"] = self.project

		for d in frappe.db.get_list("Imprest Advance", filters=filters, fields=["posting_date"]):
			date_obj = datetime.datetime.strptime(str(d.posting_date), "%Y-%m-%d")
			year_old = date_obj.year
			if str(year) == str(year_old):
				frappe.throw("Imprest Advance already taken for branch <b>{}</b>, imprest type <b>{}</b>{}".format(
					self.branch,
					self.imprest_type,
					", and project <b>{}</b>".format(self.project) if self.project else ""
				))

	def check_imprest_amount(self):
		query = """
			SELECT imp.imprest_limit
			FROM `tabBranch Imprest Item` imp
			WHERE imp.parent = %(branch)s
				AND imp.imprest_type = %(imprest_type)s
				{project_condition}
		"""
		query_params = {'branch': self.branch, 'imprest_type': self.imprest_type}
		project_condition = ''

		# if self.project:
		# 	project_condition = 'AND imp.project = %(project)s'
		# 	query_params['project'] = self.project

		query = query.format(project_condition=project_condition)
		result = frappe.db.sql(query, query_params, as_dict=True)

		if not result or not result[0].get('imprest_limit'):
			branch_link = frappe.utils.get_link_to_form('Branch', self.branch)
			frappe.throw('Please assign Imprest Limit in Branch: {} under Imprest Settings Section'.format(branch_link))
		
		# for d in result:
		# 	if d.project and not self.project:
		# 		frappe.throw("This imprest type <b>{}</b> is assigned to a Project but you have not selected a Project".format(self.imprest_type))
		
		imprest_limit = result[0].get('imprest_limit')
		
		message = "Amount requested cannot be greater than Imprest Limit <b>{}</b> for branch <b>{}</b> and imprest type <b>{}</b>".format(imprest_limit, self.branch, self.imprest_type)
		if self.project:
			message += " and project <b>{}</b>".format(self.project)

		if self.amount > imprest_limit:
			frappe.throw(message)

	def before_cancel(self):
		if self.journal_entry:
			je_status = frappe.get_value("Journal Entry", {"name": self.journal_entry}, "docstatus")
			if cint(je_status) == 1:
				frappe.throw("Journal Entry {} for this transaction needs to be cancelled first".format(frappe.get_desk_link("Journal Entry", self.journal_entry)))
			else:
				frappe.db.sql("delete from `tabJournal Entry` where name = '{}'".format(self.journal_entry))
				self.db_set("journal_entry", None)

	def on_submit(self):
		if cint(self.first_advance) == 1:
			notify_workflow_states(self)
		if not self.is_opening:
			self.post_journal_entry()

	def on_cancel(self):
		if self.first_advance == 0 and self.imprest_recoup:
			frappe.throw("Imprest Recoup <b>{}</b> needs to to cancelled first.".format(self.imprest_recoup))
		
		self.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry")
		if cint(self.first_advance) == 1:
			notify_workflow_states(self)

	def post_journal_entry(self):
		if not self.amount:
			frappe.throw(_("Amount should be greater than zero"))

		query = """
			SELECT comp.imprest_advance_account, br.expense_bank_account
			FROM `tabCompany` comp
			LEFT JOIN `tabBranch` br ON br.name = %(branch)s
			WHERE comp.name = %(company)s
		"""
		result = frappe.db.sql(query, {'branch': self.branch, 'company': self.company}, as_dict=True)

		if not result or not result[0].get('imprest_advance_account'):
			frappe.throw("Setup Default Imprest Advance Account in Company Settings")
		
		if not result[0].get('expense_bank_account'):
			frappe.throw("Setup Expense Bank Account in <b>{}</b> Branch".format(self.branch))

		debit_account = result[0].get('imprest_advance_account')
		credit_account = result[0].get('expense_bank_account')

		voucher_type = "Journal Entry"
		voucher_series = "Journal Voucher"
		party_type = ""
		party = ""

		debit_account_type = frappe.db.get_value("Account", debit_account, "account_type")
		credit_account_type = frappe.db.get_value("Account", credit_account, "account_type")

		if credit_account_type == "Bank":
			voucher_type = "Bank Entry"
			voucher_series = "Bank Payment Voucher"

		if debit_account_type in ("Payable", "Receivable"):
			party_type = self.party_type
			party = self.party

		remarks = []
		if self.remarks:
			remarks.append(_("Note: {0}").format(self.remarks))

		remarkss = "".join(remarks)

		# Posting Journal Entry
		je = frappe.new_doc("Journal Entry")

		je.update({
			"doctype": "Journal Entry",
			"voucher_type": voucher_type,
			"naming_series": voucher_series,
			"title": "Imprest Advance - " + self.name,
			"user_remark": remarkss if remarkss else "Note: " + "Imprest Advance - " + self.name,
			"posting_date": self.posting_date,
			"company": self.company,
			"total_amount_in_words": money_in_words(self.amount),
			"branch": self.branch
		})

		je.append("accounts", {
			"account": debit_account,
			"debit_in_account_currency": self.amount,
			"cost_center": self.cost_center,
			"project": self.project,
			"reference_type": "Imprest Advance",
			"reference_name": self.name,
			"party_type": party_type,
			"party": party
		})
		
		je.append("accounts", {
			"account": credit_account,
			"credit_in_account_currency": self.amount,
			"cost_center": self.cost_center,
			"project": self.project,
		})

		je.insert()
		# Set a reference to the claim journal entry
		self.db_set("journal_entry", je.name)
		frappe.msgprint("Journal Entry created. {}".format(frappe.get_desk_link("Journal Entry", je.name)))
	
def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	# if user == "Administrator" or "System Manager" in user_roles or "Accounts User" in user_roles or "Account Manager" in user_roles: 
	if any(role in user_roles for role in {"Administrator", "System Manager", "Accounts User", "Account Manager"}):
		return

	return """(
		owner = '{user}'
		or
		(approver = '{user}' and workflow_state not in  ('Draft','Rejected','Cancelled'))
	)""".format(user=user)
