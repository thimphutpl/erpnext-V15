# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class CustomerTrack(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		branch: DF.Link | None
		c1_status: DF.Link | None
		c2_status: DF.Link | None
		cid_number: DF.Data | None
		co_status: DF.Link | None
		country: DF.Data | None
		customer_details: DF.SmallText | None
		customer_id: DF.Link
		customer_name: DF.Data | None
		customer_report: DF.LongText | None
		customer_status: DF.Literal["", "C0", "C1", "C2", "Completed"]
		customer_type: DF.Data | None
		email_id: DF.Data | None
		phone_number: DF.Data | None
		primary_address: DF.Data | None
		salutation: DF.Data | None
		warranty: DF.Link | None
	# end: auto-generated types
	def validate(self):
		pass
def set_missing_values(source, target_doc):
	# if target_doc.doctype == "Purchase Order" and getdate(target_doc.schedule_date) < getdate(
	# 	nowdate()
	# ):
	# 	target_doc.schedule_date = None
	target_doc.customer_track_id = source.name
	# target_doc.run_method("set_missing_values")
	# target_doc.run_method("calculate_taxes_and_totals")

@frappe.whitelist()
def make_c0_status(source_name, target_doc=None, args=None):
	if args is None:
		args = {}

	def postprocess(source, target_doc):
		# if frappe.flags.args and frappe.flags.args.default_supplier:
		# 	# items only for given default supplier
		# 	supplier_items = []
		# 	for d in target_doc.items:
		# 		default_supplier = get_item_defaults(d.item_code, target_doc.company).get("default_supplier")
		# 		if frappe.flags.args.default_supplier == default_supplier:
		# 			supplier_items.append(d)
		# 	target_doc.items = supplier_items
		# source.co_status = target_doc.name
		set_missing_values(source, target_doc)


	doclist = get_mapped_doc(
		"Customer Track",
		source_name,
		{
			"Customer Track": {
				"doctype": "C0 Status",
				"validation": {"docstatus": ["=", 0], "customer_status": ["=", "C0"]},
			}
		},
		target_doc,
		postprocess,
		
	)

	return doclist

@frappe.whitelist()
def make_c1_status(source_name, target_doc=None, args=None):
	if args is None:
		args = {}

	def postprocess(source, target_doc):
		# if frappe.flags.args and frappe.flags.args.default_supplier:
		# 	# items only for given default supplier
		# 	supplier_items = []
		# 	for d in target_doc.items:
		# 		default_supplier = get_item_defaults(d.item_code, target_doc.company).get("default_supplier")
		# 		if frappe.flags.args.default_supplier == default_supplier:
		# 			supplier_items.append(d)
		# 	target_doc.items = supplier_items
		# source.c1_status = target_doc.name
		set_missing_values(source, target_doc)


	doclist = get_mapped_doc(
		"Customer Track",
		source_name,
		{
			"Customer Track": {
				"doctype": "C1 Status",
				"validation": {"docstatus": ["=", 0], "customer_status": ["=", "C1"]},
			}
		},
		target_doc,
		postprocess,
		
	)

	return doclist

@frappe.whitelist()
def make_c2_status(source_name, target_doc=None, args=None):
	if args is None:
		args = {}

	def postprocess(source, target_doc):
		# if frappe.flags.args and frappe.flags.args.default_supplier:
		# 	# items only for given default supplier
		# 	supplier_items = []
		# 	for d in target_doc.items:
		# 		default_supplier = get_item_defaults(d.item_code, target_doc.company).get("default_supplier")
		# 		if frappe.flags.args.default_supplier == default_supplier:
		# 			supplier_items.append(d)
		# 	target_doc.items = supplier_items
		# source.c2_status = target_doc.name
		set_missing_values(source, target_doc)


	doclist = get_mapped_doc(
		"Customer Track",
		source_name,
		{
			"Customer Track": {
				"doctype": "C2 Status",
				"validation": {"docstatus": ["=", 0], "customer_status": ["=", "C2"]},
			}
		},
		target_doc,
		postprocess,
		
	)

	return doclist

@frappe.whitelist()
def make_warranty(source_name, target_doc=None, args=None):
	if args is None:
		args = {}

	def postprocess(source, target_doc):
		# if frappe.flags.args and frappe.flags.args.default_supplier:
		# 	# items only for given default supplier
		# 	supplier_items = []
		# 	for d in target_doc.items:
		# 		default_supplier = get_item_defaults(d.item_code, target_doc.company).get("default_supplier")
		# 		if frappe.flags.args.default_supplier == default_supplier:
		# 			supplier_items.append(d)
		# 	target_doc.items = supplier_items
		# source.warranty = target_doc.name
		set_missing_values(source, target_doc)


	doclist = get_mapped_doc(
		"Customer Track",
		source_name,
		{
			"Customer Track": {
				"doctype": "Warranty",
				"validation": {"docstatus": ["=", 0], "customer_status": ["=", "On Warranty"]},
			}
		},
		target_doc,
		postprocess,
		
	)

	return doclist
@frappe.whitelist()
def make_customer_track(source_name, target_doc=None):
	def update_date(obj, target, source_parent):
		return

	def transfer_currency(obj, target, source_parent):
		return
		
	def adjust_last_date(source, target):
		return

	doc = get_mapped_doc("Customer Track", source_name, {
			"Customer Track": {
				"doctype": "C0 Status",
				"field_map": {
					"name": "c0_status",
					"customer_id": "customer_id",
					"company": "company",
					"customer_name": "customer_name",
				},
				"postprocess": update_date,
				"validation": {"docstatus": ["=", 0]}
			},
			"Hostel Asset Maintenance": {
				"doctype": "Hostel Maintenance Item",
				"postprocess": transfer_currency,
			},
		}, target_doc, adjust_last_date)
	return doc