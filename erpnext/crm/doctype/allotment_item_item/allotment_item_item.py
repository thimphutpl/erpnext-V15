# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AllotmentItemItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		c2_status: DF.Link | None
		customer_details: DF.SmallText | None
		customer_id: DF.Link | None
		customer_name: DF.Data | None
		customer_report: DF.LongText | None
		email_id: DF.Data | None
		item_code: DF.Link | None
		item_name: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		phone_number: DF.Data | None
		price_costing: DF.Link | None
		primary_address: DF.Data | None
		purchase_order: DF.Link | None
		qty: DF.Int
		rate: DF.Currency
		responsible_branch: DF.Data | None
		sales_order: DF.Link | None
		salutation: DF.Data | None
		select: DF.Check
		tvo_numbervc_numbervi_number: DF.Data | None
	# end: auto-generated types
	pass
