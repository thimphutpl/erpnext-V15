# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class POLReceiveItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		allocated_amount: DF.Float
		amount: DF.Float
		balance: DF.Float
		balance_amount: DF.Float
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		pol_advance: DF.Link | None
		serial_and_batch_bundle: DF.Link | None
	# end: auto-generated types
	pass
