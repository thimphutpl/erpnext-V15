# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class ReappropriationDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		amount: DF.Currency
		budget_against: DF.Literal["Cost Center", "Project"]
		company: DF.Link | None
		fiscal_year: DF.Link | None
		from_account: DF.Link | None
		from_cost_center: DF.Link | None
		from_month: DF.Link | None
		from_project: DF.Link | None
		posting_date: DF.Date | None
		reference: DF.Data | None
		to_account: DF.Link | None
		to_cost_center: DF.Link | None
		to_month: DF.Link | None
		to_project: DF.Link | None
	# end: auto-generated types
	pass
