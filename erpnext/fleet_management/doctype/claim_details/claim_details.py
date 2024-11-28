# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class ClaimDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		claim_amount: DF.Float
		claim_date: DF.Date
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		remarks: DF.LongText | None
	# end: auto-generated types
	pass
