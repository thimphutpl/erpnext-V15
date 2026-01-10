# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, get_link_to_form, flt, date_diff, cint, nowdate


class ContractDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.cms.doctype.contract_revised_detail.contract_revised_detail import ContractRevisedDetail
		from frappe.types import DF

		actual_amount: DF.Data | None
		actual_completion_date: DF.Date | None
		additional: DF.Data | None
		completion_date: DF.SmallText | None
		contract_name: DF.SmallText
		currency: DF.Link
		defect_liability_amount: DF.Literal["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
		delay_days: DF.Data | None
		discount: DF.Data | None
		end_date: DF.Date | None
		exchange_rate: DF.Data | None
		final_amount: DF.Data
		focal_person: DF.Link
		focal_person_name: DF.Data | None
		initial_amount: DF.Data
		negotiation_amount: DF.Data | None
		reference_number: DF.Data
		revised_expiry_date: DF.Date | None
		start_date: DF.Date
		status: DF.Literal["Active", "Closed", "Terminated"]
		supplier: DF.Link
		supplier_name: DF.Data | None
		supplier_type: DF.Literal["", "Domestic Vendor", "Indian Vendor", "International Vendor"]
		table_fwbc: DF.Table[ContractRevisedDetail]
		types_of_contract: DF.Literal["", "Goods", "Service", "Works"]
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
		self.calculate_delay_days()

	def validate_dates(self):
		if self.start_date and self.end_date:
			if getdate(self.start_date) > getdate(self.end_date):
				frappe.throw("Start Date cannot be greater than End Date.")

		if self.revised_expiry_date and self.end_date:
			if getdate(self.revised_expiry_date) < getdate(self.end_date):
				frappe.throw("Revised Expiry Date cannot be before Contract End Date.")
		if self.actual_completion_date and self.start_date:
			if getdate(self.actual_completion_date) < getdate(self.start_date):
				frappe.throw("Actual Completion Date cannot be before Contract Start Date.")

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
		if not self.initial_amount:
			frappe.throw("Initial Amount is required")
		self.final_amount = (
			flt(self.initial_amount)
			- flt(self.discount)
			- flt(self.negotiation_amount)
			+ flt(self.additional)
		)


	def calculate_delay_days(self):
		if not self.actual_completion_date:
			self.delay_days = 0
			return

		deadline = self.revised_expiry_date or self.end_date
		if not deadline:
			self.delay_days = 0
			return

		actual = getdate(self.actual_completion_date)
		deadline = getdate(deadline)

		delay = date_diff(actual, deadline)
		self.delay_days = cint(delay) if delay > 0 else 0



