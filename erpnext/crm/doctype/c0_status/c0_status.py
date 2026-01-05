# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class C0Status(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		customer_id: DF.Link | None
		customer_name: DF.Data | None
		customer_report: DF.LongText | None
		customer_track_id: DF.Link | None
		email_id: DF.Data | None
		id_card_no: DF.Data | None
		inquiry: DF.LongText | None
		phone_number: DF.Data | None
		response: DF.LongText | None
		responsible_branch: DF.Link | None
		salutation: DF.Data | None
	# end: auto-generated types

	def validate(self):
		if self.customer_track_id:
			frappe.db.sql("update `tabCustomer Track` set co_status = '{}' where name = '{}'".format(self.name, self.customer_track_id))

@frappe.whitelist()
def make_c0_status(source_name, target_doc=None):
	def update_date(obj, target, source_parent):
		return

	def transfer_currency(obj, target, source_parent):
		return
		
	def adjust_last_date(source, target):
		return

	doc = get_mapped_doc("C0 Status", source_name, {
			"C0 Status": {
				"doctype": "C1 Status",
				"field_map": {
					"name": "c1_status",
					"customer_id": "customer_id",
					"company": "company",
					"customer_name": "customer_name",
				},
				"postprocess": update_date,
				"validation": {"docstatus": ["=", 1]}
			},
			"Hostel Asset Maintenance": {
				"doctype": "Hostel Maintenance Item",
				"postprocess": transfer_currency,
			},
		}, target_doc, adjust_last_date)
	return doc			