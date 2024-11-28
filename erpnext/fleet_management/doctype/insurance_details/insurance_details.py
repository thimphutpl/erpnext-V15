# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class InsuranceDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		due_date: DF.Date
		insurance_company: DF.Link
		insurance_type: DF.Literal["", "Third Party", "Comprehensive"]
		insured_amount: DF.Currency
		insured_date: DF.Date
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		policy_number: DF.Data
		validity: DF.Date | None
	# end: auto-generated types
	pass
