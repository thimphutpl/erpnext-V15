# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Warranty(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.crm.doctype.warranty_details.warranty_details import WarrantyDetails
		from frappe.types import DF

		allotted_amount: DF.Data | None
		customer_details: DF.SmallText | None
		customer_id: DF.Data | None
		customer_name: DF.Data | None
		customer_report: DF.LongText | None
		customer_track_id: DF.Link | None
		email_id: DF.Data | None
		item: DF.Data | None
		phone_number: DF.Data | None
		primary_address: DF.Data | None
		responsible_branch: DF.Link | None
		serial_no: DF.Link | None
		table_ufus: DF.Table[WarrantyDetails]
		valid_to: DF.Date | None
	# end: auto-generated types

	def validate(self):
		if self.customer_track_id:
			frappe.db.sql("update `tabCustomer Track` set warranty = '{}' where name = '{}'".format(self.name, self.customer_track_id))
