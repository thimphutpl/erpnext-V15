# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from frappe.model.document import Document
import frappe
import re
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, get_datetime, get_url, nowdate, now_datetime


class Branch(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.branch_bank_account.branch_bank_account import BranchBankAccount
		from frappe.types import DF
		from hrms.hr.doctype.branch_imprest_item.branch_imprest_item import BranchImprestItem

		abbr: DF.Data | None
		address: DF.LongText | None
		branch: DF.Data
		branch_bank_account: DF.Table[BranchBankAccount]
		company: DF.Link
		cost_center: DF.Link
		disabled: DF.Check
		expense_bank_account: DF.Link | None
		gis_policy_number: DF.Data | None
		holiday_list: DF.Link | None
		imprest_limit: DF.Currency
		items: DF.Table[BranchImprestItem]
		letter_head: DF.Link | None
		revenue_bank_account: DF.Link | None
	# end: auto-generated types

	def validate(self):
		self.validate_amounts()
		self.update_gis_policy_no()
		self.check_duplicates()

	def validate_amounts(self):
		for i in self.items:
			if flt(i.imprest_limit) < 0:
				frappe.throw(_("Row#{0} : Imprest limit cannot be less than zero.").format(i.idx),title="Invalid Data")

	def update_gis_policy_no(self):
		# Following code commented due to performance issue
		if self.get_db_value("gis_policy_number") != self.gis_policy_number:
			frappe.db.sql("""
					update `tabEmployee`
					set gis_policy_number = '{1}'
					where branch = '{0}'
			""".format(self.name, self.gis_policy_number))

	def check_duplicates(self):
		dup = {}
		# Checking for duplicates in imprest settings
		for i in self.items:
			if i.imprest_type in dup:
				frappe.throw(_("Duplicate values found for Imprest Type <b>`{0}`</b>").format(i.imprest_type),title="Duplicate Values")
			else:
				dup.update({i.imprest_type: 1})
				if i.default:
					# if dup.has_key('default'):
					if 'default' in dup:
						dup.update({'duplicate': 1})
							
					dup.update({'default': 1})

		# Checking for duplicate defaults in imprest settings
		if dup:
			# if dup.has_key('duplicate'):
			if 'duplicate' in dup:
				frappe.throw(_("Only one imprest type can be default."),title="Duplicate Values")
		