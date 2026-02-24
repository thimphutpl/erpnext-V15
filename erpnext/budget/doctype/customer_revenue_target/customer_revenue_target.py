# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from frappe import _
from frappe.utils import flt

class CustomerRevenueTarget(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.revenue_target_customer.revenue_target_customer import RevenueTargetCustomer
		from frappe.types import DF

		amended_from: DF.Link | None
		attachment: DF.Attach | None
		company: DF.Link
		cost_center: DF.Link | None
		fiscal_year: DF.Link
		revenue_target_customer: DF.Table[RevenueTargetCustomer]
		title: DF.Data | None
		tot_adjustment_amount: DF.Currency
		tot_net_target_amount: DF.Currency
		tot_target_amount: DF.Currency

	def validate(self):
		self.validate_mandatory()
		self.calculate_targets()
		self.set_initial_revenue_target()
	def validate_mandatory(self):
		for item in self.revenue_target_customer:
			if flt(item.target_amount) < 0.0:
				frappe.throw(_("Row#{0}: Target Amount cannot be a negative value.").format(item.idx), title="Invalid Value")
	
	def calculate_targets(self):
		tot_target_amount = flt(0.0)
		for d in self.revenue_target_customer:
			tot_target_amount += flt(d.target_amount)
		self.tot_target_amount = tot_target_amount
		
	@frappe.whitelist()
	def get_customer(self):
		query = "select name as customer, customer_type from `tabCustomer` where disabled=0"
		entries = frappe.db.sql(query, as_dict=True)
		self.set('revenue_target_customer', [])

		for d in entries:
			row = self.append('revenue_target_customer', {})
			row.update(d)

	@frappe.whitelist()
	def set_initial_revenue_target(self):
		total_target = 0
		for d in self.revenue_target_customer:
			initial_target = flt(d.january) + flt(d.february) + flt(d.march) + flt(d.april)+ flt(d.may) +flt(d.june) +flt(d.july) +flt(d.august) + flt(d.september) +flt(d.october) +flt(d.november) +flt(d.december)
			total_target += flt(initial_target)
			d.db_set("target_amount", initial_target)
			self.db_set("tot_target_amount", total_target)		