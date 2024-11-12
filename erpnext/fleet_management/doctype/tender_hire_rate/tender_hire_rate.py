# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TenderHireRate(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		customer: DF.Link
		equipment_model: DF.Link
		equipment_type: DF.Link
		from_date: DF.Date
		idle_rate: DF.Float
		to_date: DF.Date
		with_fuel: DF.Float
		without_fuel: DF.Float
	# end: auto-generated types
	pass
