# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CustomerOrderVehicle(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		contact_no: DF.ReadOnly | None
		driver_cid: DF.ReadOnly | None
		drivers_name: DF.ReadOnly | None
		noof_truck_load: DF.Int
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		quantity: DF.Float
		vehicle: DF.Link | None
		vehicle_capacity: DF.ReadOnly | None
	# end: auto-generated types
	pass
