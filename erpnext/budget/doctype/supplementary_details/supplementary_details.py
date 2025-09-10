# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class SupplementaryDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link
		amended_from: DF.Link | None
		amount: DF.Currency
		budget_against: DF.Literal["", "Cost Center", "Project"]
		company: DF.Link | None
		cost_center: DF.Link | None
		fiscal_year: DF.Link | None
		month: DF.Link | None
		posting_date: DF.Date
		project: DF.Link | None
		reference: DF.Link
	# end: auto-generated types
	pass
