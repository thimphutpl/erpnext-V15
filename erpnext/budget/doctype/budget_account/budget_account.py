# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class BudgetAccount(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link
		budget_amount: DF.Currency
		budget_check: DF.Literal["Stop", "Ignore"]
		budget_received: DF.Currency
		budget_sent: DF.Currency
		budget_type: DF.Link
		initial_budget: DF.Currency
		parent: DF.Data
		parent_account: DF.Link | None
		parentfield: DF.Data
		parenttype: DF.Data
		remarks: DF.SmallText | None
		supplementary_budget: DF.Currency
	# end: auto-generated types
	pass
