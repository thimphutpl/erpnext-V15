# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DeliveryConfirmation(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link | None
		confirmation_status: DF.Literal["In Transit", "Received", "Cancelled"]
		contact_no: DF.Data | None
		customer: DF.Link | None
		customer_order: DF.Link | None
		delivery_note: DF.Link | None
		drivers_name: DF.Data | None
		exit_date_time: DF.Datetime
		qty: DF.Float
		received_date_time: DF.Datetime | None
		remarks: DF.Data | None
		transport_mode: DF.Literal["Common Pool", "Self Owned Transport", "Others", "Private Pool"]
		user: DF.Link | None
		vehicle: DF.Link | None
	# end: auto-generated types
	pass
