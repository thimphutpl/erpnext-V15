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
		commission: DF.Currency
		cost_of_fuel_tank: DF.Currency
		custom_commision: DF.Currency
		custom_duty: DF.Currency
		declaration_and_processing_fee: DF.Currency
		excise_duty: DF.Currency
		finance__and_overhead_charges: DF.Currency
		freight: DF.Currency
		gst: DF.Currency
		insurance: DF.Currency
		items: DF.Table[PriceCostingItem]
		labour_charges: DF.Currency
		margin_and_handling_charges: DF.Currency
		marine_insurance: DF.Currency
		marketing_expenses: DF.Currency
		other_collection_and_charges: DF.Currency
		overhead_and_other_cost: DF.Currency
		pdi_expenses: DF.Currency
		posting_date: DF.Date
		price_costing_name: DF.Data
		purchase_type: DF.Literal["", "Air Order", "Sea Order", "Full Container", "By Road"]
		selling_charges: DF.Currency
		service_charges: DF.Currency
		stock_holding_cost: DF.Currency
		total_source_rate: DF.Float
		transit_insurance: DF.Currency
		transportation_charges: DF.Currency
	# end: auto-generated types
	pass

	def validate(self):
		self.calculate_charges()

	def calculate_charges(self):
		self.total_source_rate = sum((i.source_rate or 0) for i in self.items)
		for i in self.items:
			i.insurance = self.calculate_value(self.insurance, i.source_rate)
			i.freight = self.calculate_value(self.freight, i.source_rate)
			i.gst = self.calculate_value(self.gst, i.source_rate)
			i.custom_duty = self.calculate_value(self.custom_duty, i.source_rate)
			i.excise_duty = self.calculate_value(self.excise_duty, i.source_rate)
			i.service_charges = self.calculate_value(self.service_charges, i.source_rate)
			i.clearing_and_forwarding_charges = self.calculate_value(self.clearing_and_forwarding_charges, i.source_rate)
			i.bank_charges = self.calculate_value(self.bank_charges, i.source_rate)
			i.transportation_charges = self.calculate_value(self.transportation_charges, i.source_rate)
			i.labour_charges = self.calculate_value(self.labour_charges, i.source_rate)

			i.landed_cost = flt(i.source_rate + i.insurance + i.freight + i.gst + i.custom_duty + i.excise_duty + i.service_charges + i.clearing_and_forwarding_charges + i.bank_charges + i.transportation_charges + i.labour_charges, 2)


			# if (i.processing_percent):
			i.processing_amount = flt(i.landed_cost * ((i.processing_percent if i.processing_percent else 0)/100), 2)

			# if (i.bank_charges_percent):
			i.bank_charges_amount = flt(i.landed_cost * ((i.bank_charges_percent if i.bank_charges_percent else 0)/100), 2)

			# if (i.stock_holding_percent):
			i.stock_holding_amount = flt(i.landed_cost * ((i.stock_holding_percent if i.stock_holding_percent else 0)/100), 2)

			# if (i.margin_percent):
			i.margin_amount = flt(i.landed_cost * ((i.margin_percent if i.margin_percent else 0)/100), 2)
			
			i.selling_price = flt(i.landed_cost + i.processing_amount + i.bank_charges_amount + i.stock_holding_amount + i.margin_amount, 2)

	def calculate_value(self, value, source_rate):
		return flt(value * (source_rate/self.total_source_rate), 2)
