# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class ServiceSalesJobcard(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.model.document import Document
		from frappe.types import DF

		address: DF.SmallText | None
		allocated_amount: DF.Data | None
		amended_from: DF.Link | None
		balance_amount: DF.Data | None
		branch: DF.Link
		chassis_number: DF.Link | None
		cost_center: DF.Data | None
		customer_group: DF.Data | None
		customer_id: DF.Link
		customer_name: DF.Data | None
		end_date: DF.Date
		items: DF.Table[Document]
		jobcard_report: DF.LongText | None
		jobcard_status: DF.Literal["Ongoing", "Completed"]
		jocard_type: DF.Link | None
		location: DF.Link | None
		mobile_no: DF.Data | None
		payable_amount: DF.Currency
		posting_date: DF.Date
		set_warehouse: DF.Link | None
		start_date: DF.Date
		table_vvwk: DF.Table[Document]
		vehicle_number: DF.Data | None
		warehouse: DF.Data | None
		warranty_id: DF.Link | None
	# end: auto-generated types
	# pass

	def validate(self):
		total_payable = 0
		for item in self.items:
			item.amount = item.rate * item.quantity
			total_payable += item.amount
		self.payable_amount = total_payable	

		# --- STATUS CONTROL ---
		if self.jobcard_status == "Ongoing" and self.docstatus == 1:
			frappe.throw("You cannot submit a Jobcard while the status is Ongoing. Please change status to COMPLETED.")
	
	def before_submit(self):
		if self.jobcard_status == "Ongoing":
			frappe.throw("You cannot submit while Jobcard Status is Ongoing. Change to COMPLETED first.")

	def on_submit(self):
		self.update_serial_no_used_amount()

	def update_serial_no_used_amount(self):
		
		# chassis_no = self.chassis_number
		# payable = self.payable_amount

		# if chassis_no and payable:
		# 	sn_name = frappe.db.get_value("Serial No", chassis_no, "name")

		# 	if sn_name:
		# 		sn_doc = frappe.get_doc("Serial No", sn_name)
		# 		sn_doc.used_amount = payable
		# 		sn_doc.save(ignore_permissions=True)
		# 	else:
		# 		frappe.log_error(
		# 			f"Serial No '{chassis_no}' not found for update.",
		# 			"Service Sales Jobcard Update Error"
		# 		)

		serial_no = self.chassis_number
		payable_amount = self.payable_amount

		if not serial_no:
			frappe.throw("Chassis Number is required to continue.")

		# Fetch Serial No details
		sn = frappe.db.get_value(
			"Serial No",
			serial_no,
			["name", "balance_amount"],
			as_dict=True
		)

		if not sn:
			frappe.throw(f"Serial No '{serial_no}' does not exist in the system.")

		# If balance_amount is zero → Stop submission
		if self.jocard_type == "Free Services" and sn.balance_amount == 0:
			frappe.throw(f"Balance Amount is ZERO for Serial No: {serial_no}. You cannot submit this Jobcard.")

		# --- AUTO UPDATE used_amount ONLY IF validation passed ---
		if payable_amount:
			sn_doc = frappe.get_doc("Serial No", serial_no)
			sn_doc.used_amount = payable_amount
			sn_doc.save(ignore_permissions=True)

@frappe.whitelist()
def make_service_sales_jobcard(source_name, target_doc=None):
	def update_date(obj, target, source_parent):
		return

	def transfer_currency(obj, target, source_parent):
		return
		
	def adjust_last_date(source, target):
		return

	doc = get_mapped_doc("Service Sales Jobcard", source_name, {
			"Service Sales Jobcard": {
				"doctype": "Sales Order",
				"field_map": {
					"customer_id": "customer",
					"set_warehouse":"set_warehouse",
				
				},
				"postprocess": update_date,
				"validation": {"docstatus": ["=", 1]}
			},
			"Jobcard Service Details": {
				"doctype": "Sales Order Item",
				"field_map": {
					"quantity": "qty",
					"amount":"rate"
				},
				"postprocess": transfer_currency,
			},
		}, target_doc, adjust_last_date)
	return doc			