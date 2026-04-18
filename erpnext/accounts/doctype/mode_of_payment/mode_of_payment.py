# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.model.document import Document
from frappe import _

class ModeofPayment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.mode_of_payment_account.mode_of_payment_account import ModeofPaymentAccount
		from frappe.types import DF

		accounts: DF.Table[ModeofPaymentAccount]
		credit_allowed: DF.Check
		is_lc: DF.Check
		mode_of_payment: DF.Data
		type: DF.Literal["Cash", "Bank", "General"]
	# end: auto-generated types
	def validate(self):
		self.validate_accounts()
		self.validate_repeating_companies()
	
	def validate_repeating_companies(self):
		"""Error when Same Company is entered multiple times in accounts"""
		accounts_list = []
		for entry in self.accounts:
			accounts_list.append(entry.company)

		if len(accounts_list)!= len(set(accounts_list)):
			frappe.throw(_("Same Company is entered more than once"))

	def validate_accounts(self):
		for entry in self.accounts:
			"""Error when Company of Ledger account doesn't match with Company Selected"""
			if entry.default_account:
				if frappe.db.get_value("Account", entry.default_account, "company") != entry.company:
					frappe.throw(_("Account does not match with Company"))
