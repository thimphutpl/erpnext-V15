# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt

class C1Status(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.crm.doctype.customer_quotation_details.customer_quotation_details import CustomerQuotationDetails
		from frappe.types import DF

		amended_from: DF.Link | None
		c1_status_report: DF.LongText | None
		customer_details: DF.SmallText | None
		customer_id: DF.Link | None
		customer_name: DF.Data | None
		customer_report: DF.LongText | None
		customer_track_id: DF.Link | None
		dob: DF.Date | None
		dzongkhag: DF.Data | None
		email_id: DF.Data | None
		footer: DF.SmallText | None
		gewog: DF.Data | None
		grand_total: DF.Float
		header: DF.SmallText | None
		id_card_no: DF.Data | None
		items: DF.Table[CustomerQuotationDetails]
		phone_number: DF.Data | None
		posting_date: DF.Date
		presently_residing_at: DF.Data | None
		primary_address: DF.Data | None
		responsible_branch: DF.Link | None
		salutation: DF.Data | None
		terms_and_cond_tempate: DF.Link | None
		terms_and_conditions: DF.TextEditor | None
		village: DF.Data | None
	# end: auto-generated types

	def validate(self):
		self.check_item()
		# self.check_quantity()
		total_payable = 0
		for item in self.items:
			item.net_price = flt(item.amount) - flt(item.discount_amount)
			total_payable += item.net_price
		self.grand_total = total_payable

		if self.customer_track_id:
			frappe.db.sql("update `tabCustomer Track` set c1_status = '{}' where name = '{}'".format(self.name, self.customer_track_id))

	def check_item(self):
		if not self.items:
			frappe.throw("No items found")

	# def check_quantity(self):
	# 	for i in self.items:
	# 		if i.quantity:
	# 			frappe.throw("No items found")

@frappe.whitelist()
def make_c1_status(source_name, target_doc=None):
	def update_date(obj, target, source_parent):
		return

	def transfer_currency(obj, target, source_parent):
		return
		
	def adjust_last_date(source, target):
		return

	doc = get_mapped_doc("C1 Status", source_name, {
			"C1 Status": {
				"doctype": "C2 Status",
				"field_map": {
					"name": "c2_status",
					"customer_id": "customer_id",
					"company": "company",
					"customer_name": "customer_name",
				},
				"postprocess": update_date,
				"validation": {"docstatus": ["=", 1]}
			},
			"Customer Quotation Details": {
				"doctype": "Order Confirmation Details",
				"field_map": {
					"amount": "gross_price",
					"rate": "rate",
				},
				"postprocess": transfer_currency,
			},
		}, target_doc, adjust_last_date)
	return doc

@frappe.whitelist()
def get_item_rate(price_costing, item):
	if not item:
		frappe.throw("Select Item first")
	rate = frappe.get_value(
		"Price Costing Item",
		{"parent": price_costing, "item": item},
		"selling_price"
	)
	return rate

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_items(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""
        SELECT t1.name, t1.price_costing_name, t1.purchase_type, t1.posting_date
        FROM `tabPrice Costing` t1
		INNER JOIN `tabPrice Costing Item` t2
		ON t1.name = t2.parent
        WHERE t2.item = %(item_code)s
        AND t1.name LIKE %(txt)s
        AND t1.price_costing_name LIKE %(txt)s
        AND t1.purchase_type LIKE %(txt)s
        AND t1.posting_date LIKE %(txt)s
		AND t2.docstatus = 1
    """, {
        "item_code": filters.get("item_code"),
        "txt": f"%{txt}%"
    })