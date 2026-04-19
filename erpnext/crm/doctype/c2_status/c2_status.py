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

		allotment_item: DF.Link | None
		amended_from: DF.Link | None
		confirmation_date: DF.Date
		customer_details: DF.SmallText | None
		customer_id: DF.Link | None
		customer_name: DF.Data | None
		customer_report: DF.LongText | None
		customer_track_id: DF.Link | None
		dispatch_no: DF.Data
		dob: DF.Date | None
		dzongkhag: DF.Data | None
		email_id: DF.Data | None
		gewog: DF.Data | None
		id_card_no: DF.Data | None
		order_information: DF.LongText | None
		phone_number: DF.Data | None
		presently_residing_at: DF.Data | None
		primary_address: DF.Data | None
		purchase_order: DF.Link | None
		responsible_branch: DF.Data | None
		salutation: DF.Data | None
		table_yefo: DF.Table[OrderConfirmationDetails]
		village: DF.Data | None
	# end: auto-generated types

	def validate(self):
		if self.customer_track_id:
			frappe.db.sql("update `tabCustomer Track` set c2_status = '{}' where name = '{}'".format(self.name, self.customer_track_id))
		
		# Calculate gross price for each item in table_yefo
		for row in self.table_yefo:
			row.gross_price = flt(row.rate) + flt(row.gst) + flt(row.cd) + flt(row.et) + flt(row.bst) + flt(row.gt)

@frappe.whitelist()
def make_c2_status(source_name, target_doc=None):
	def update_date(obj, target, source_parent):
		return

	def transfer_currency(obj, target, source_parent):
		return
		
	def adjust_last_date(source, target):
		return

	def update_branch_fields(obj, target, source_parent):
		# Keep your original date logic
		update_date(obj, target, source_parent)
		target.taxes_and_charges = "Advance Received From Customer"
		# Safely set cost_center and warehouse from branch
		if target.branch:
			branch_doc = frappe.get_doc("Branch", target.branch)
			target.cost_center = getattr(branch_doc, "cost_center", None)
			target.set_warehouse = getattr(branch_doc, "warehouse", None)

	def set_sales_order_item_values(source, target, source_parent):
		# Calculate gross price
		gross_price = flt(source.rate) + flt(source.gst) + flt(source.cd) + flt(source.et) + flt(source.bst) + flt(source.gt)
		
		target.rate = gross_price
		target.amount = flt(source.quantity) * gross_price
		target.base_rate = gross_price
		target.base_amount = flt(source.quantity) * gross_price
		
		# Set additional fields if needed
		if source.tvo_numbervin_numbervi_number:
			target.tvo_no = source.tvo_numbervin_numbervi_number

	doc = get_mapped_doc("C2 Status", source_name, {
			"C2 Status": {
				"doctype": "Sales Order",
				"field_map": {
					"name": "c2_status",
					"customer_id": "customer_id",
					"company": "company",
					"customer_name": "customer",
					"phone_number": "contact_person",
					"primary_address": "address",
					"name": "c2_id",
					"responsible_branch": "branch",
					"cost_center": "cost_center",
					"warehouse": "set_warehouse"
				},
				"postprocess": update_branch_fields,
				"validation": {"docstatus": ["=", 1]}
			},
			"Order Confirmation Details": {
				"doctype": "Sales Order Item",
				"field_map": {
					"quantity": "qty",
					"tvo_numbervin_numbervi_number": "tvo_no"
				},
				"field_no_map": ["discount_amount", "rate", "amount"],
				"postprocess": set_sales_order_item_values,
			},
		}, target_doc, adjust_last_date)
	return doc

@frappe.whitelist()
def create_purchase_order(source_name, target_doc=None):
	def update_date(obj, target, source_parent):
		return

	def transfer_currency(obj, target, source_parent):
		return
		
	def adjust_last_date(source, target):
		return

	def set_item_values(source, target, source_parent):
		branch_doc = frappe.get_doc("Branch", source_parent.responsible_branch)
		item_doc = frappe.get_doc("Item", source.item_code)
		
		expense_account = frappe.db.get_value(
			"Item Default",
			{"parent": source.item_code},
			"expense_account"
		)
		
		# Calculate gross price
		gross_price = flt(source.rate) + flt(source.gst) + flt(source.cd) + flt(source.et) + flt(source.bst) + flt(source.gt)
		
		target.cost_center = branch_doc.cost_center
		target.warehouse = branch_doc.warehouse
		target.uom = item_doc.stock_uom
		target.expense_account = expense_account
		target.rate = gross_price
		target.amount = flt(source.quantity) * gross_price

	def update_branch_fields(obj, target, source_parent):
		# Keep your original date logic
		update_date(obj, target, source_parent)

		# Safely set cost_center and warehouse from branch
		if target.branch:
			branch_doc = frappe.get_doc("Branch", target.branch)
			target.cost_center = getattr(branch_doc, "cost_center", None)
			target.set_warehouse = getattr(branch_doc, "warehouse", None)

	doc = get_mapped_doc("C2 Status", source_name, {
			"C2 Status": {
				"doctype": "Purchase Order",
				"field_map": {
					"name": "c2_status",
					"company": "company",
					"phone_number": "contact_person",
					"primary_address": "address",
					"name": "c2_id",
					"responsible_branch": "branch",
					"cost_center": "cost_center",
					"warehouse": "set_warehouse",
				},
				"postprocess": update_branch_fields,
				"validation": {"docstatus": ["=", 1]}
			},
			"Order Confirmation Details": {
				"doctype": "Purchase Order Item",
				"field_map": {
					"quantity": "qty",
					"tvo_numbervin_numbervi_number": "tvo_number"
				},
				"field_no_map": ["discount_amount", "rate", "amount"],
				"postprocess": set_item_values,
			},
		}, target_doc, adjust_last_date)
	return doc

# Helper function to safely convert to float
def flt(value, default=0.0):
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default