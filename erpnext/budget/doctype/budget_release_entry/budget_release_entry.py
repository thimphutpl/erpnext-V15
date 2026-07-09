# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BudgetReleaseEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link
		ad_hoc: DF.Check
		approved_budget: DF.Currency
		branch: DF.Link
		broad_head: DF.Link | None
		budget_activity: DF.Link
		budget_sub_activity: DF.Link
		company: DF.Link
		cost_center: DF.Link
		fiscal_year: DF.Link
		month: DF.Literal["", "July", "August", "September", "October", "November", "December", "January", "February", "March", "April", "May", "June"]
		monthly_release: DF.Check
		posting_date: DF.Date
		released_budget: DF.Currency
		source_of_fund: DF.Link
	# end: auto-generated types

	pass
