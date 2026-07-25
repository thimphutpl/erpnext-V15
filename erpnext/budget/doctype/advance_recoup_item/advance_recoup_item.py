# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AdvanceRecoupItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link
		amount: DF.Currency
		bill_attachment: DF.Attach | None
		broad_head: DF.Link
		budget_activity: DF.Link
		budget_sub_activity: DF.Link
		invoice_date: DF.Date | None
		invoice_no: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		remark: DF.SmallText | None
		source_of_fund: DF.Link
	# end: auto-generated types

	pass
