# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.utils import flt

class PriceCosting(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.selling.doctype.price_costing_item.price_costing_item import PriceCostingItem
		from frappe.types import DF

		amended_from: DF.Link | None
		bank_charges: DF.Currency
		clearing_and_forwarding_charges: DF.Currency
		custom_duty: DF.Currency
		excise_duty: DF.Currency
		frieght: DF.Currency
		gst: DF.Currency
		insurance: DF.Currency
		items: DF.Table[PriceCostingItem]
		labour_charges: DF.Currency
		posting_date: DF.Date
		price_costing_name: DF.Data
		purchase_type: DF.Literal["", "Air Order", "Sea Order", "Full Container"]
		service_charges: DF.Currency
		total_source_rate: DF.Currency
		transportation_charges: DF.Currency
	# end: auto-generated types
	pass

	def validate(self):
		self.calculate_charges()

	def calculate_charges(self):
		for i in self.get("items"):
			self.total_source_rate += i.source_rate

			i.insurance = self.calculate_value(self.insurance, i.source_rate)
			i.frieght = self.calculate_value(self.frieght, i.source_rate)
			i.gst = self.calculate_value(self.gst, i.source_rate)
			i.custom_duty = self.calculate_value(self.custom_duty, i.source_rate)
			i.excise_duty = self.calculate_value(self.excise_duty, i.source_rate)
			i.service_charges = self.calculate_value(self.service_charges, i.source_rate)
			i.clearing_and_forwarding_charges = self.calculate_value(self.clearing_and_forwarding_charges, i.source_rate)
			i.bank_charges = self.calculate_value(self.bank_charges, i.source_rate)
			i.transportation_charges = self.calculate_value(self.transportation_charges, i.source_rate)
			i.labour_charges = self.calculate_value(self.labour_charges, i.source_rate)

			landed_cost = flt(i.source_rate) + flt(i.insurance) + flt(i.frieght) + flt(i.gst) + flt(i.custom_duty) + flt(i.excise_duty) + flt(i.service_charges) + flt(i.clearing_and_forwarding_charges) + flt(i.bank_charges) + flt(i.transportation_charges) + flt(i.labour_charges)
			i.landed_cost = landed_cost

			if (i.processing_percent):
				i.processing_amount = landed_cost * (i.processing_percent/100)

			if (i.bank_charges_percent):
				i.bank_charges_amount = landed_cost * (i.bank_charges_percent/100)

			if (i.stock_holding_percent):
				i.stock_holding_amount = landed_cost * (i.stock_holding_percent/100)

			if (i.margin_percent):
				i.margin_amount = landed_cost * (i.margin_percent/100)
			
			i.selling_price = i.landed_cost + i.processing_amount + i.bank_charges_amount + i.stock_holding_amount + i.margin_amount

	def calculate_value(self, value, source_rate):
		return value * (source_rate/self.total_source_rate)
