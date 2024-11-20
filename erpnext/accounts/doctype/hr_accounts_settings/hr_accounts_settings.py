# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HRAccountsSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF


	# end: auto-generated types
	pass

def get_bank_account(branch=None):
	company=frappe.db.get_value("Branch",branch, "company")
	default_bank_account = frappe.db.get_value('Company',company, 'default_bank_account')
	expense_bank_account = None
	if branch:
		expense_bank_account = frappe.db.get_value('Branch', branch, 'expense_bank_account')

	if not expense_bank_account and not default_bank_account:
		frappe.throw(_("Please set <b>Bank Expense Account</b> under <b>Branch</b> master"))
	return default_bank_account if default_bank_account else expense_bank_account