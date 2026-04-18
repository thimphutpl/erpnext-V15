# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class OrderConfirmationDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		advance__remarks: DF.SmallText | None
		advances_paid: DF.Currency
		amount: DF.Currency
		bst: DF.Currency
		c1_detail: DF.Link | None
		c1_status: DF.Link | None
		cd: DF.Currency
		discount_amount: DF.Currency
		engine_cc: DF.Float
		et: DF.Currency
		fuel_type: DF.Literal["", "Petrol", "Diesel", "EV"]
		gross_price: DF.Currency
		gst: DF.Currency
		gt: DF.Currency
		gvw_tonnage: DF.Float
		item_code: DF.Link
		item_details: DF.LongText | None
		item_group: DF.Data | None
		item_name: DF.Data | None
		item_sub_group: DF.Data | None
		make: DF.Data | None
		model: DF.Data | None
		model_year: DF.Data | None
		net_price: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		price_costing: DF.Link | None
		quantity: DF.Data
		rate: DF.Currency
		seating_capacity: DF.Float
		transmission_type: DF.Literal["", "Manual", "Automatic"]
		tvo_numbervin_numbervi_number: DF.Data | None
		vehicle_color: DF.Data | None
	# end: auto-generated types
	pass
