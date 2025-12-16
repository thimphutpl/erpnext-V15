# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, get_link_to_form, flt

class ContractDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		additional: DF.Data | None
		contract_name: DF.Data
		discount: DF.Data | None
		end_date: DF.Date
		final_amount: DF.Data
		focal_person: DF.Link
		focal_person_name: DF.Data | None
		initial_amount: DF.Data
		reference_number: DF.Data
		revised_expiry_date: DF.Date | None
		start_date: DF.Date
		supplier: DF.Link
		supplier_name: DF.Data | None
		supplier_type: DF.Literal["", "Domestic Vendor", "Indian Vendor", "International Vendor"]
	# end: auto-generated types
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		additional: DF.Data | None
		contract_name: DF.Data
		discount: DF.Data | None
		end_date: DF.Date
		final_amount: DF.Data
		focal_person: DF.Link
		focal_person_name: DF.Data | None
		initial_amount: DF.Data
		reference_number: DF.Data
		start_date: DF.Date
		supplier: DF.Link
		supplier_name: DF.Data | None
		supplier_type: DF.Literal["", "Domestic Vendor", "Indian Vendor", "International Vendor"]

	def validate(self):
		self.validate_dates()
		self.validate_reference_number()
		self.calculate_final_amount()

	def validate_dates(self):
		if self.start_date and self.end_date:
			if getdate(self.start_date) > getdate(self.end_date):
				frappe.throw("Start Date cannot be greater than End Date.")

	def validate_reference_number(self):
		if not self.reference_number:
			frappe.throw("Reference Number is Required")
		existing = frappe.db.get_value(
			"Contract Details",
			{"reference_number": self.reference_number, "name": ("!=", self.name)},
			"name"
		)		
		if existing:
			link = get_link_to_form("Contract Details", existing)
			frappe.throw(
				("Reference Number <b>{0}</b> already exists in document {1}.").format(
					self.reference_number, link
				)
			)
	def calculate_final_amount(self):
		discount = addition =0
		if not self.initial_amount:
			frappe.throw("Initial Amount Is required")
		if self.discount:
			discount = self.discount
		if self.additional:
			addition = self.additional
		self.final_amount = flt(self.initial_amount) - flt(discount) + flt(addition)