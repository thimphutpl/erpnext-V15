# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AdvanceItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		apply_retention: DF.Check
		apply_tds: DF.Check
		budget_activity: DF.Link
		budget_sub_activity: DF.Link
		opening_balance: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		particular: DF.SmallText | None
		retention: DF.Link | None
		retention_account: DF.Data | None
		retention_amount: DF.Currency
		retention_rate: DF.Currency
		source_of_fund: DF.Link
		tds: DF.Link | None
		tds_account: DF.Data | None
		tds_amount: DF.Currency
		tds_rate: DF.Currency
		total_amount: DF.Currency
	# end: auto-generated types

	pass
