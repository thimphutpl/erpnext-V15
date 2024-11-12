# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from frappe.model.document import Document
import frappe
import re


class Branch(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.branch_bank_account.branch_bank_account import BranchBankAccount
		from frappe.types import DF
		from hrms.hr.doctype.branch_imprest_item.branch_imprest_item import BranchImprestItem

		abbreviation: DF.Data | None
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
		if not self.get("__islocal"):
			self.validate_branch_abbreviation()

	def validate_branch_abbreviation(self):
		if not re.match(r'^[A-Z]{3}$', self.abbreviation):
			frappe.throw("Branch abbreviation must be exactly three uppercase alphabet letters")
