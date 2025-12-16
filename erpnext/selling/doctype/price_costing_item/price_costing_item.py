# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class PriceCostingItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		bank_charges: DF.Currency
		bank_charges_amount: DF.Currency
		bank_charges_percent: DF.Percent
		clearing_and_forwarding_charges: DF.Currency
		custom_duty: DF.Currency
		description: DF.Data | None
		excise_duty: DF.Currency
		frieght: DF.Currency
		gst: DF.Currency
		insurance: DF.Currency
		item: DF.Link | None
		item_name: DF.Data | None
		labour_charges: DF.Currency
		landed_cost: DF.Currency
		margin_amount: DF.Currency
		margin_percent: DF.Percent
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		processing_amount: DF.Currency
		processing_percent: DF.Percent
		selling_price: DF.Currency
		service_charges: DF.Currency
		source_rate: DF.Currency
		stock_holding_amount: DF.Currency
		stock_holding_percent: DF.Percent
		transportation_charges: DF.Currency
	# end: auto-generated types
	pass
