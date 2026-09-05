# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MobilisationEntryItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link | None
		advance_amount: DF.Currency
		advance_type: DF.Data | None
		allocated_amount: DF.Currency
		balance_amount: DF.Currency
		budget_activity: DF.Link | None
		budget_sub_activity: DF.Link | None
		is_opening: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		reference: DF.Link | None
		source_of_fund: DF.Link | None
		total_amount: DF.Currency
	# end: auto-generated types

	pass
