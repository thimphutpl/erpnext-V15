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
		hire_charge_amount: DF.Float
		hsd_consumption: DF.Currency
		idle_rate: DF.Currency
		number_of_days: DF.Int
		operator_salary: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		project: DF.ReadOnly | None
		rate_type: DF.Data | None
		registration_number: DF.Data
		total_amount: DF.Currency
		vehicle_logbook: DF.Link
	# end: auto-generated types
	pass
