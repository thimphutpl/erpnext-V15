# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.selling_controller import SellingController
from erpnext.accounts.general_ledger import make_reverse_gl_entries
from frappe.utils import flt


class ServiceSalesJobcard(SellingController):
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
		company: DF.Link | None
		contact_number: DF.Data | None
		contact_person: DF.Data | None
		cost_center: DF.Data | None
		customer_group: DF.Data | None
		customer_id: DF.Link
		customer_name: DF.Data | None
		customer_request: DF.SmallText | None
		delayed_date_from: DF.Date | None
		delayed_date_to: DF.Date | None
		delayed_reason: DF.LongText | None
		delivery_date_from: DF.Date | None
		delivery_date_to: DF.Date | None
		end_date: DF.Date
		items: DF.Table[Document]
		jobcard_report: DF.LongText | None
		jobcard_status: DF.Literal["Ongoing", "Delayed", "Waiting for Spareparts Divison", "Spareparts Delivered", "Completed"]
		jobcard_type: DF.Link | None
		km_reading: DF.Data | None
		location: DF.Link | None
		mobile_no: DF.Data | None
		payable_amount: DF.Currency
		posting_date: DF.Date
		requesting_branch: DF.Link | None
		requesting_cost_center: DF.Data | None
		set_warehouse: DF.Link | None
		spareparts_branch: DF.Link | None
		spareparts_remarks: DF.LongText | None
		start_date: DF.Date
		supplier_order: DF.Data | None
		table_fspm: DF.Table[Document]
		table_vvwk: DF.Table[Document]
		used_amount: DF.Data | None
		vehicle_number: DF.Data | None
		warehouse: DF.Data | None
		warranty_id: DF.Link | None
		workorder: DF.Data | None
	# end: auto-generated types
	# pass

	def validate(self):
		total_payable = 0
		for item in self.items:
			item.amount = item.rate * item.quantity
			total_payable += item.amount
		self.payable_amount = total_payable	
		if self.jobcard_type == "Free Services":
			self.validate_free_services()
			self.used_amount == flt(self.allocated_amount)/2

		# --- STATUS CONTROL ---
		if self.jobcard_status == "Ongoing" and self.docstatus == 1:
			frappe.throw("You cannot submit a Jobcard while the status is Ongoing. Please change status to COMPLETED.")
	
	def before_submit(self):
		if self.jobcard_status == "Ongoing":
			frappe.throw("You cannot submit while Jobcard Status is Ongoing. Change to COMPLETED first.")

	def on_submit(self):
		self.update_serial_no_used_amount()
		# self.make_gl_entries()

		# Check if selected Jobcard Type has inter_company = 1
		inter_company = frappe.db.get_value(
			"Jobcard Type",
			self.jobcard_type,
			"inter_company"
		)
		# customer_group = frappe.db.get_value(
		# 	"Customer",
		# 	self.customer_id,
		# 	"customer_group"
		# )

		if inter_company or self.jobcard_type == "Free Services":
			self.make_gl_entries()
			# self.get_gl_entries()
		if self.jobcard_type == "Free Services":
			self.update_service_count_in_serial_no()

		self.update_km_in_serial_no()

	def on_cancel(self):
		self.cancel_gl_entries()

	def cancel_gl_entries(self):
		make_reverse_gl_entries(
			voucher_type=self.doctype,
			voucher_no=self.name
		)
	
	def validate_free_services(self):
		count = frappe.db.count(
			"Service Sales Jobcard",
			{"chassis_number": self.chassis_number, "jocard_type": "Free Services"}
		)

		if count >= 2:
			frappe.throw("Two Free Services for Chassis No is completed")
			# frappe.throw(_("Two Free Services for Chassis No. {0} is completed").format(self.chassis_number))

	def update_km_in_serial_no(self):
		frappe.db.set_value(
			"Serial No",
			self.chassis_number,
			{
				"km_reading": self.km_reading,
			}
		)

	def update_service_count_in_serial_no(self):
		# count = frappe.db.get_value(
		# 	"Service Sales Jobcard",
		# 	{"chassis_number": self.chassis_number, "jocard_type": "Free Services"},
		# 	"free_services_count"
		# )
		used_amount, allotted_amount, free_services_count = frappe.db.get_value(
			"Serial No",
			self.chassis_number,
			["used_amount", "allotted_amount", "free_services_count"]
		) or (0, 0)

		frappe.db.set_value(
			"Serial No",
			self.chassis_number,
			{
				"free_services_count": free_services_count + 1,
				"used_amount": used_amount + (allotted_amount/2),
				# "balance_amount": balance_amount - (allotted_amount/2)
			}
		)

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
		if self.jobcard_type == "Free Services" and sn.balance_amount == 0:
			frappe.throw(f"Balance Amount is ZERO for Serial No: {serial_no}. You cannot submit this Jobcard.")

		# --- AUTO UPDATE used_amount ONLY IF validation passed ---
		# if payable_amount:
		# 	sn_doc = frappe.get_doc("Serial No", serial_no)
		# 	sn_doc.used_amount = payable_amount
		# 	sn_doc.save(ignore_permissions=True)

	def make_gl_entries(self, gl_entries=None, from_repost=False):
		from erpnext.accounts.general_ledger import make_gl_entries, make_reverse_gl_entries
		
		if not gl_entries:
			gl_entries = self.get_gl_entries()
		
		if gl_entries:
			if self.docstatus == 1:
				make_gl_entries(
					gl_entries,
					update_outstanding="No",
					merge_entries=False,
					from_repost=from_repost,
				)

	def get_gl_entries(self, warehouse_account=None):
		gl_entries = []
		self.make_customer_gl_entries(gl_entries)
		self.make_income_gl_entries(gl_entries)
		return gl_entries

	def make_customer_gl_entries(self, gl_entries):
		"""Create debit entry for customer receivable"""
		# Check if selected Jobcard Type has inter_company = 1
		inter_company = frappe.db.get_value(
			"Jobcard Type",
			self.jobcard_type,
			"inter_company"
		)
		default_deferred_revenue_account = frappe.get_cached_value('Company', self.company, 'default_deferred_revenue_account')
		
		if not inter_company and not default_deferred_revenue_account:
			frappe.throw(f"Default Receivable Account not set for Company: {self.company}")

		jobcard_expense_account = frappe.get_cached_value("Cost Center", self.requesting_cost_center, "jobcard_expense_account")
		
		if inter_company and not jobcard_expense_account:
			frappe.throw(f"Revenue Account not set for Cost Center: {self.requesting_cost_center}")

		jobcard_expense_account = frappe.get_cached_value("Branch", self.requesting_cost_center, "jobcard_expense_account")
		
		# if inter_company and not jobcard_expense_account:
		# 	frappe.throw(f"Revenue Account not set for Cost Center: {self.requesting_cost_center}")
		
		# payable_account = 
		
		gl_entries.append(
			self.get_gl_dict(
				{
					"account": default_deferred_revenue_account if not inter_company or self.jobcard_type == "Free Services"  else jobcard_expense_account,
					"party_type": "Customer",
					"party": self.customer_id,
					"debit": self.payable_amount if self.jobcard_type != "Free Services" else flt(self.allocated_amount)/2,
					"debit_in_account_currency": self.payable_amount if self.jobcard_type != "Free Services" else flt(self.allocated_amount)/2,
					"against": self.cost_center,
					"cost_center": self.cost_center,
					"voucher_type": self.doctype,
					"voucher_no": self.name,
					"against_voucher_type": self.doctype,
					"against_voucher": self.name,
				}
			)
		)

	def make_income_gl_entries(self, gl_entries):
		"""Create credit entry for income account"""
		income_account = frappe.get_cached_value("Cost Center", self.cost_center, "revenue_account")
		
		if not income_account:
			frappe.throw(f"Revenue Account not set for Cost Center: {self.cost_center}")
		
		gl_entries.append(
			self.get_gl_dict(
				{
					"account": income_account,
					"credit": self.payable_amount if self.jobcard_type != "Free Services" else flt(self.allocated_amount)/2,
					"credit_in_account_currency": self.payable_amount if self.jobcard_type != "Free Services" else flt(self.allocated_amount)/2,
					"against": self.customer_id,
					"cost_center": self.cost_center,
					"voucher_type": self.doctype,
					"voucher_no": self.name,
				}
			)
		)					

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
					"name": "service_sales_jobcard",
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
				"condition": lambda doc: doc.status == "Completed",
				"postprocess": transfer_currency,
			},
		}, target_doc, adjust_last_date)
	return doc			

@frappe.whitelist()
def make_spare_sales_jobcard(source_name, target_doc=None):
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
					"name": "service_sales_jobcard",
					"customer_id": "customer",
					"set_warehouse":"set_warehouse",
					"spareparts_branch":"branch",
				},
				"postprocess": update_date,
				"validation": {"docstatus": ["=", 1]}
			},
			"Jobcard Spareparts Details": {
				"doctype": "Sales Order Item",
				"field_map": {
					"quantity": "qty",
					"amount":"rate",
					"price_costing":"price_template"
				},
				"condition": lambda doc: doc.status == "Available",
				"postprocess": transfer_currency,
			},
		}, target_doc, adjust_last_date)
	return doc			