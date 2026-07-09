# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from erpnext.accounts.utils import validate_field_number
import frappe
from frappe.utils import cint
from frappe import throw, _
from frappe.utils.nestedset import NestedSet, get_ancestors_of, get_descendants_of
class RootNotEditable(frappe.ValidationError): pass

class MiscellaneousAccount(NestedSet):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account_code: DF.Data | None
		account_currency: DF.Link | None
		account_number: DF.Data | None
		account_type: DF.Literal["", "Bank", "Cash", "Expense Account", "Fixed Asset", "Income Account", "Payable", "Receivable", "Temporary"]
		balance_must_be: DF.Literal["", "Debit", "Credit"]
		bank_account_no: DF.Data | None
		bank_account_type: DF.Link | None
		bank_branch: DF.Link | None
		bank_name: DF.Link | None
		cash_flow_account: DF.Check
		cce_account: DF.Check
		company: DF.Link
		disabled: DF.Check
		freeze_account: DF.Literal["No", "Yes"]
		include_in_gross: DF.Check
		inter_company_account: DF.Check
		is_an_advance_account: DF.Check
		is_group: DF.Check
		lft: DF.Int
		old_parent: DF.Data | None
		parent_miscellaneous_account: DF.Link | None
		report_type: DF.Literal["", "Balance Sheet", "Profit and Loss"]
		rgt: DF.Int
		root_type: DF.Literal["", "Asset", "Liability", "Income", "Expense", "Equity"]
		sws_account_name: DF.Data
		tax_rate: DF.Float
	# end: auto-generated types

	def validate(self):
		self.validate_parent()
		self.validate_root_details()
		validate_field_number("Miscellaneous Account", self.name, self.account_number, self.company, "account_number")
		self.validate_group_or_ledger()
		self.set_root_and_report_type()
		self.validate_mandatory()
		self.validate_root_company_and_sync_account_to_children()
		self.validate_bank_details()
	def autoname(self):
		# from erpnext.accounts.utils import get_autoname_with_number
		# self.name = get_autoname_with_number(self.account_number, self.account_name, None, self.company)
		self.name = self.sws_account_name


	def validate_bank_details(self):
		if self.bank_branch and not self.bank_name:
			frappe.throw(_('Please select proper Bank under Bank Account Details'))
		elif self.bank_branch:
			if frappe.db.get_value('Financial Institution Branch', self.bank_branch, 'financial_institution') \
					!= self.bank_name:
				frappe.throw(_('Invalid Branch under Bank Account Details'))
	def validate_mandatory(self):
		if not self.root_type:
			throw(_("Root Type is mandatory"))

		if not self.report_type:
			throw(_("Report Type is mandatory"))
	def on_trash(self):
		# checks gl entries and if child exists
		if self.check_gle_exists():
			throw(_("Account with existing transaction can not be deleted"))

		super(MiscellaneousAccount, self).on_trash(True)
	def validate_parent(self):
		"""Fetch Parent Details and validate parent account"""
		if self.parent_miscellaneous_account:
			par = frappe.db.get_value("Miscellaneous Account", self.parent_miscellaneous_account,
				["name", "is_group", "company"], as_dict=1)
			if not par:
				throw(_("Account {0}: Parent account {1} does not exist").format(self.name, self.parent_miscellaneous_account))
			elif par.name == self.name:
				throw(_("Account {0}: You can not assign itself as parent account").format(self.name))
			elif not par.is_group:
				throw(_("Account {0}: Parent account {1} can not be a ledger").format(self.name, self.parent_miscellaneous_account))
			elif par.company != self.company:
				throw(_("Account {0}: Parent account {1} does not belong to company: {2}")
					.format(self.name, self.parent_miscellaneous_account, self.company))

	def validate_root_details(self):
		# does not exists parent
		if frappe.db.exists("Miscellaneous Account", self.name):
			if not frappe.db.get_value("Miscellaneous Account", self.name, "parent_miscellaneous_account"):
				throw(_("Root cannot be edited."), RootNotEditable)

		if not self.parent_miscellaneous_account and not self.is_group:
			frappe.throw(_("The root account {0} must be a group").format(frappe.bold(self.name)))
	def validate_group_or_ledger(self):
		if self.get("__islocal"):
			return

		existing_is_group = frappe.db.get_value("Miscellaneous Account", self.name, "is_group")
		if cint(self.is_group) != cint(existing_is_group):
			if self.check_gle_exists():
				throw(_("Account with existing transaction cannot be converted to ledger"))
			elif self.is_group:
				if self.account_type and not self.flags.exclude_account_type_check:
					throw(_("Cannot covert to Group because Account Type is selected."))
			elif self.check_if_child_exists():
				throw(_("Account with child nodes cannot be set as ledger"))
	def set_root_and_report_type(self):
		if self.parent_miscellaneous_account:
			par = frappe.db.get_value("Miscellaneous Account", self.parent_miscellaneous_account,
				["report_type", "root_type"], as_dict=1)

			if par.report_type:
				self.report_type = par.report_type
			if par.root_type:
				self.root_type = par.root_type

		if self.is_group:
			db_value = frappe.db.get_value("Miscellaneous Account", self.name, ["report_type", "root_type"], as_dict=1)
			if db_value:
				if self.report_type != db_value.report_type:
					frappe.db.sql("update `tabMiscellaneous Account` set report_type=%s where lft > %s and rgt < %s",
						(self.report_type, self.lft, self.rgt))
				if self.root_type != db_value.root_type:
					frappe.db.sql("update `tabMiscellaneous Account` set root_type=%s where lft > %s and rgt < %s",
						(self.root_type, self.lft, self.rgt))

		if self.root_type and not self.report_type:
			self.report_type = "Balance Sheet" \
				if self.root_type in ("Asset", "Liability", "Equity") else "Profit and Loss"
	def validate_root_company_and_sync_account_to_children(self):
		# ignore validation while creating new compnay or while syncing to child companies
		ancestors = get_root_company(self.company)
		if ancestors:
			if not frappe.db.get_value("Miscellaneous Account",
				{'sws_account_name': self.sws_account_name, 'company': ancestors[0]}, 'name'):
				frappe.throw(_("Please add the account to root level Company - %s" % ancestors[0]))
		elif self.parent_miscellaneous_account:
			descendants = get_descendants_of('Company', self.company)
			if not descendants: return
			parent_acc_name_map = {}
			parent_acc_name, parent_acc_number = frappe.db.get_value('Miscellaneous Account', self.parent_miscellaneous_account, \
				["miscellaneous_account_name", "account_number"])
			filters = {
				"company": ["in", descendants],
				"sws_account_name": parent_acc_name,
			}
			if parent_acc_number:
				filters["account_number"] = parent_acc_number

			for d in frappe.db.get_values('Miscellaneous Account', filters=filters, fieldname=["company", "name"], as_dict=True):
				parent_acc_name_map[d["company"]] = d["name"]
			if not parent_acc_name_map: return
	def check_gle_exists(self):
		return frappe.db.get_value("SWS GL Entry", {"account": self.name})

	def check_if_child_exists(self):
		return frappe.db.sql("""select name from `tabMiscellaneous Account` where parent_miscellaneous_account = %s
			and docstatus != 2""", self.name)
	@frappe.whitelist()
	def convert_ledger_to_group(self):
		if self.check_gle_exists():
			throw(_("Account with existing transaction can not be converted to group."))
		elif self.account_type and not self.flags.exclude_account_type_check:
			throw(_("Cannot covert to Group because Account Type is selected."))
		else:
			self.is_group = 1
			self.save()
			return 1
	@frappe.whitelist()
	def convert_group_to_ledger(self):
		if self.check_if_child_exists():
			throw(_("Account with child nodes cannot be converted to ledger"))
		elif self.check_gle_exists():
			throw(_("Account with existing transaction cannot be converted to ledger"))
		else:
			self.is_group = 0
			self.save()
			return 1

@frappe.whitelist()
def merge_account(old, new, is_group, root_type, company):
	# Validate properties before merging
	if not frappe.db.exists("Miscellaneous Account", new):
		throw(_("Miscellaneous Account {0} does not exist").format(new))

	val = list(frappe.db.get_value("Miscellaneous Account", new,
		["is_group", "root_type", "company"]))

	if val != [cint(is_group), root_type, company]:
		throw(_("""Merging is only possible if following properties are same in both records. Is Group, Root Type, Company"""))

	if is_group and frappe.db.get_value("Miscellaneous Account", new, "parent_miscellaneous_account") == old:
		frappe.db.set_value("Miscellaneous Account", new, "parent_miscellaneous_account",
			frappe.db.get_value("Miscellaneous Account", old, "parent_miscellaneous_account"))

	frappe.rename_doc("Miscellaneous Account", old, new, merge=1, force=1)

	return new

@frappe.whitelist()
def get_root_company(company):
	# return the topmost company in the hierarchy
	ancestors = get_ancestors_of('Company', company, "lft asc")
	return [ancestors[0]] if ancestors else []