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

		advance: DF.Data | None
		amended_from: DF.Link | None
		bill_amount_in_currency: DF.Data | None
		branch: DF.Link | None
		contract: DF.Link
		contract_name: DF.SmallText | None
		cost_center: DF.Link | None
		currency: DF.Link
		exchange_rate: DF.Data
		final_amount: DF.Data | None
		initial_amount: DF.Data | None
		ld: DF.Data | None
		net_amount_payable: DF.Data | None
		payable_amount: DF.Data | None
		payment: DF.Literal["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "Final"]
		payment_date: DF.Date | None
		payment_type: DF.Literal["", "Advance", "Retention Money", "Milestone", "RA Bill"]
		posting_date: DF.Date
		reference_number: DF.Data | None
		retention_money: DF.Data | None
		supplier: DF.Link | None
		supplier_name: DF.Data | None
		supplier_type: DF.Literal["", "Domestic Vendor", "Indian Vendor", "International Vendor"]
		tds: DF.Data | None
		total_deduction: DF.Data | None
	# end: auto-generated types
	def validate(self):
		self.calculate_amount_in_btn()
		self.validate_duplicate_payment()

	def before_submit(self):
		self.validate_duplicate_payment()

	def validate_duplicate_payment(self):
		if (self.payment_type or "").strip() not in ("Milestone", "RA Bill"):
			return
		if not self.contract or not self.branch or not self.payment_type or not self.payment:
			return

		filters = {
			"contract": self.contract,
			"branch": self.branch,
			"payment_type": self.payment_type,
			"payment": self.payment,
			"docstatus": ["<", 2],
		}

		existing = frappe.get_all(
			"Contract Payment",
			filters=filters,
			fields=["name", "docstatus"],
			limit=1,
		)
		if existing:
			existing_name = existing[0]["name"]
			if existing_name != self.name:
				frappe.throw(
					f"Duplicate Contract Payment not allowed.<br>"
					f"Already exists: <b>{existing_name}</b><br>"
					f"Contract: <b>{self.contract}</b>, Branch: <b>{self.branch}</b>, "
					f"Payment Type: <b>{self.payment_type}</b>, Payment: <b>{self.payment}</b>"
				)	
	
	def calculate_amount_in_btn(self):
		if not self.bill_amount_in_currency:
			frappe.throw("Bill amount in currency is required")
		if self.currency == "BTN":
			self.exchange_rate = 1
			self.payable_amount = flt(self.bill_amount_in_currency)
			return
		if not self.exchange_rate:
			frappe.throw("Exchange Rate is required")
		self.payable_amount = flt(self.bill_amount_in_currency) * flt(self.exchange_rate)
