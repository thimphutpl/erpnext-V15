# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ContractPayment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		bill_amount_in_currency: DF.Data | None
		contract: DF.Link
		contract_name: DF.Data | None
		currency: DF.Link
		exchange_rate: DF.Data
		final_amount: DF.Data | None
		initial_amount: DF.Data | None
		payable_amount: DF.Data | None
		payment: DF.Literal["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "Final"]
		payment_date: DF.Date | None
		payment_type: DF.Literal["", "Advance", "Mobilization Advance", "Material Advance", "Milestone", "RA Bill"]
		posting_date: DF.Date
		reference_number: DF.Data | None
		supplier: DF.Link | None
		supplier_name: DF.Data | None
		supplier_type: DF.Literal["", "Domestic Vendor", "Indian Vendor", "International Vendor"]
	# end: auto-generated types
	def validate(self):
		self.calculate_amount_in_btn()
	
	def calculate_amount_in_btn(self):
		if self.currency !="BTN":
			if not self.exchange_rate:
				frappe.throw("Exchange Rate is required")
			if not self.bill_amount_in_currency:
				frappe.throw("Bill amount in currency is required")
			self.payable_amount = flt(self.bill_amount_in_currency)* flt(self.exchange_rate)
		else:
			if not self.bill_amount_in_currency:
				frappe.throw("Bill amount in currency is required")
			self.payable_amount = self.bill_amount_in_currency