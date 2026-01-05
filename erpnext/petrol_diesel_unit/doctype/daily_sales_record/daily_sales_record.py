# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from frappe.model.document import Document


class DailySalesRecord(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.model.document import Document
		from frappe.types import DF

		amended_from: DF.Link | None
		amount: DF.Currency
		bill_sales: DF.Table[Document]
		bill_sales_amount: DF.Currency
		bill_sales_quantity: DF.Float
		branch: DF.Data | None
		employee: DF.Link | None
		employee_name: DF.Data | None
		item_code: DF.Data | None
		item_name: DF.Data | None
		nozzle_1: DF.Float
		nozzle_2: DF.Float
		nozzle_3: DF.Float
		nozzle_4: DF.Float
		posting_date: DF.Date
		quantity_sold: DF.Float
		rate: DF.Currency
		shift: DF.Link
		shift_from_time: DF.Data | None
		shift_to_time: DF.Data | None
		total_amount: DF.Currency
		total_quantity_sold: DF.Data | None
		ug_tank: DF.Link
		warehouse: DF.Data | None
	# end: auto-generated types
	def validate(self):
		self.calculate_totals()

	def on_submit(self):
		self.update_ug_tank()

	@frappe.whitelist()
	def calculate_totals(self):
		self.bill_sales_amount = self.bill_sales_quantity = 0
		for a in self.bill_sales:
			a.bill_sales  = a.quantity * self.rate
			self.bill_sales_quantity += flt(a.quantity,2)
			self.bill_sales_amount += flt(a.amount,2)
		return self.bill_sales_quantity, self.bill_sales_amount

	def update_ug_tank(self):
		doc = frappe.get_doc("UG Tank", self.ug_tank)
		doc.nozzle_1 = self.nozzle_1
		doc.nozzle_2 = self.nozzle_2
		doc.nozzle_3 = self.nozzle_3
		doc.nozzle_4 = self.nozzle_4
		doc.save()



	@frappe.whitelist()
	def get_item_rate(self):
		self.item_code = frappe.db.get_value("UG Tank", self.ug_tank, "item_code")
		if not self.posting_date:
			frappe.throw("Please set Posting Date")
		rate = frappe.db.sql("select price_list_rate from `tabItem Price` where selling = 1 and '{0}' >= valid_from and case when valid_upto is not null then  '{0}' <= valid_upto else 1 = 1 end and item_code = '{1}' order by creation desc limit 1".format(self.posting_date, self.item_code), as_dict=1)
		if rate:
			rate = rate[0].price_list_rate
		else:
			rate = 0
		return rate

