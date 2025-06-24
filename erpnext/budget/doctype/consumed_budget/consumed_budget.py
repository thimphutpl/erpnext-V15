# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class ConsumedBudget(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link
		amended_from: DF.Link | None
		amount: DF.Currency
		com_ref: DF.Link | None
		company: DF.Link | None
		consumed_cost_center: DF.Link | None
		cost_center: DF.Link
		item_code: DF.Link | None
		project: DF.Link | None
		reference_date: DF.Date | None
		reference_id: DF.Data | None
		reference_no: DF.Data
		reference_type: DF.Data
	# end: auto-generated types
	pass
