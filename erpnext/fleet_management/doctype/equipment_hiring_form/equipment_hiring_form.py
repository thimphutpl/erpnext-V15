# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EquipmentHiringForm(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link | None
		company: DF.Link
		contact_number: DF.Data | None
		cost_center: DF.Link | None
		end_date: DF.Date
		equipment: DF.Link
		equipment_model: DF.Data | None
		equipment_number: DF.Data | None
		equipment_type: DF.Data | None
		hiring_status: DF.Check
		rate: DF.Currency
		rate_based_on: DF.Literal["", "Daily", "Kilometer", "Lumpsum", "Per Hour", "Per Pack"]
		reading_based_on: DF.Data | None
		request_date: DF.Date
		start_date: DF.Date
		supplier: DF.Link | None
		target_hour: DF.Int
		tc_name: DF.Link | None
		terms: DF.TextEditor | None
		workflow_state: DF.Link | None
	# end: auto-generated types
	pass
