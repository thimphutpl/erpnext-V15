# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class VehicleLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		date: DF.Date
		distance: DF.Data | None
		driver_name: DF.Data | None
		from_km_reading: DF.Data | None
		from_place: DF.Data
		from_time: DF.Time | None
		idle_time: DF.Float
		operator: DF.Link | None
		operator_salary: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		pol_issued: DF.Data | None
		purpose: DF.Text
		time: DF.Data | None
		to_km_reading: DF.Data | None
		to_place: DF.Data | None
		to_time: DF.Time | None
		work_time: DF.Float
	# end: auto-generated types
	pass
