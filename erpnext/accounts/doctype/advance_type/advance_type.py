# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AdvanceType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		advance_account: DF.Link
		advance_name: DF.Data | None
		company: DF.Link | None
		company_abbr: DF.Data | None
		party_type: DF.Literal["", "Employee", "Supplier", "Customer"]
	# end: auto-generated types

	pass
