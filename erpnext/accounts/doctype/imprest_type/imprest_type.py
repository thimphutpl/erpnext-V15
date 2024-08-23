# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class ImprestType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.imprest_type_account.imprest_type_account import ImprestTypeAccount
		from frappe.types import DF

		accounts: DF.Table[ImprestTypeAccount]
		description: DF.SmallText | None
		imprest_max_limit: DF.Currency
		type: DF.Data
	# end: auto-generated types
	pass
