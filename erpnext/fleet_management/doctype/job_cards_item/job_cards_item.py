# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class JobCardsItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		checked_by: DF.Link | None
		imprest: DF.Check
		job: DF.Link
		job_name: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		quantity: DF.Float
		stock_entry: DF.Link | None
		total_amount: DF.Currency
		which: DF.Literal["", "Service", "Item"]
	# end: auto-generated types
	pass
