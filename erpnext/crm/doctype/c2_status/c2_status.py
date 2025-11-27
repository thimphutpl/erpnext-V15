# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class C2Status(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.crm.doctype.order_confirmation_details.order_confirmation_details import OrderConfirmationDetails
		from frappe.types import DF

		amended_from: DF.Link | None
		customer_details: DF.SmallText | None
		customer_id: DF.Data | None
		customer_name: DF.Data | None
		customer_report: DF.LongText | None
		customer_track_id: DF.Link | None
		email_id: DF.Data | None
		order_information: DF.LongText | None
		phone_number: DF.Data | None
		primary_address: DF.Data | None
		responsible_branch: DF.Data | None
		salutation: DF.Data | None
		table_yefo: DF.Table[OrderConfirmationDetails]
	# end: auto-generated types

	def validate(self):
		if self.customer_track_id:
			frappe.db.sql("update `tabCustomer Track` set c2_status = '{}' where name = '{}'".format(self.name, self.customer_track_id))

@frappe.whitelist()
def make_c2_status(source_name, target_doc=None):
	def update_date(obj, target, source_parent):
		return

	def transfer_currency(obj, target, source_parent):
		return
		
	def adjust_last_date(source, target):
		return

	doc = get_mapped_doc("C2 Status", source_name, {
			"C2 Status": {
				"doctype": "Sales Order",
				"field_map": {
					"name": "sales_order",
					"customer_id": "customer_id",
					"company": "company",
					"customer_name": "customer",
					"phone_number": "contact_person",
					"primary_address": "address",
					"name": "c2_id"
				},
				"postprocess": update_date,
				"validation": {"docstatus": ["=", 1]}
			},
			"Order Confirmation Details": {
				"doctype": "Sales Order Item",
				"field_map": {
					"quantity": "qty",
					"amount":"rate"
				},
				"postprocess": transfer_currency,
			},
		}, target_doc, adjust_last_date)
	return doc