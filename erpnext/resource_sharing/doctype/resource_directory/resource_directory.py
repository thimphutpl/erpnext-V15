# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ResourceDirectory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.resource_sharing.doctype.resource_available.resource_available import ResourceAvailable
		from frappe.types import DF

		adjustable_sitting_capacity: DF.Data | None
		capacity: DF.Data | None
		chasis_number: DF.Data | None
		contact_no: DF.Data | None
		cost_center: DF.Link
		custodiam_contact_number: DF.Data | None
		custodian: DF.Link | None
		custodian_email_address: DF.Data | None
		custodian_name: DF.Data | None
		discription: DF.Data | None
		engine_number: DF.Data | None
		fuel_book: DF.Data | None
		model: DF.Data | None
		quanity: DF.Data | None
		remarks: DF.Data | None
		resource: DF.Table[ResourceAvailable]
		resource_name: DF.Data | None
		resource_type: DF.Link | None
		specialisation: DF.Data | None
		status: DF.Literal["Available", "Not Available"]
		vehicle_type: DF.Data | None
	# end: auto-generated types
	pass
