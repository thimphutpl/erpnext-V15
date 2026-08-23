# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MOFEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link | None
		amount: DF.Currency
		board_head: DF.Link | None
		branch: DF.Link | None
		company: DF.Link | None
		cost_center: DF.Link | None
		mof_payment: DF.Link | None
		party: DF.DynamicLink | None
		party_type: DF.Literal["", "Employee", "Customer", "Supplier"]
		positing_date: DF.Date | None
		voucher_no: DF.DynamicLink | None
		voucher_type: DF.Link | None
	# end: auto-generated types

	pass
