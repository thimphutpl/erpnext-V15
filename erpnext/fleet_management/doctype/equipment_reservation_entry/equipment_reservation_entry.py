# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EquipmentReservationEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_form: DF.Link | None
		ehf_name: DF.Data | None
		equipment: DF.Literal["Equipment"]
		from_date: DF.Date
		from_time: DF.Time | None
		hours: DF.Data | None
		place: DF.Data | None
		reason: DF.Literal["", "Hire", "Maintenance"]
		to_date: DF.Date
		to_time: DF.Time | None
	# end: auto-generated types
	pass
