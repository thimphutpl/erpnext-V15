# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AdvanceType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.advance_type_account.advance_type_account import AdvanceTypeAccount
		from frappe.types import DF

		accounts: DF.Table[AdvanceTypeAccount]
		description: DF.SmallText | None
		max_limit: DF.Currency
		type: DF.Data
	# end: auto-generated types
	pass
