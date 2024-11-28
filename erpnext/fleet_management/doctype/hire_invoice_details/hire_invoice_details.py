# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HireInvoiceDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount_idle: DF.Currency
		amount_work: DF.Currency
		equipment: DF.Link
		idle_rate: DF.Currency
		number_of_days: DF.Int
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		rate_type: DF.Data
		registration_number: DF.Data
		total_amount: DF.Currency
		total_idle_hours: DF.Data
		total_work_hours: DF.Data
		vehicle_logbook: DF.Link
		work_rate: DF.Currency
	# end: auto-generated types
	pass
