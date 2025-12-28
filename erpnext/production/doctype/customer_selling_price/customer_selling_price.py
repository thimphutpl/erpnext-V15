# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint


class CustomerSellingPrice(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.production.doctype.selling_price_rate.selling_price_rate import SellingPriceRate
		from frappe.types import DF

		branch: DF.Link
		company: DF.Link
		customer: DF.Link
		from_date: DF.Date
		item_rates: DF.Table[SellingPriceRate]
		to_date: DF.Date
	# end: auto-generated types

	def validate(self):
		self.check_sp_rate()
		self.check_duplicate_settings()

	def check_sp_rate(self):
		for a in self.item_rates:
			if not flt(a.selling_price) > 0:
				frappe.throw(
					"Selling Rate should be greater than 0 for <b>{}</b>".format(a.particular)
				)

			if a.price_based_on == "Item":
				a.item_name = frappe.db.get_value("Item", a.particular, "item_name")
				a.timber_type = None
				a.item_sub_group = None
			else:
				a.item_name = None

	def check_duplicate_settings(self):
		item_list = []

		# Duplicate check within same document
		for a in self.item_rates:
			rate_dtl = (
				str(a.particular) + "/" +
				str(a.timber_type) + "/" +
				str(a.item_sub_group)
			)

			if rate_dtl in item_list:
				frappe.throw(
					"<b>{}, {}</b> already defined more than once".format(
						a.particular, a.item_name
					)
				)

			item_list.append(rate_dtl)

		# Check customer + branch duplicate across documents
		for a in frappe.db.sql("""
			SELECT b.branch, b.name
			FROM `tabCustomer Selling Price` b
			WHERE b.name != %s
			AND b.branch = %s
			AND (
				%s BETWEEN b.from_date AND b.to_date
				OR %s BETWEEN b.from_date AND b.to_date
				OR (%s > b.from_date AND %s < b.to_date)
				OR (%s < b.from_date AND %s > b.to_date)
			)
			AND b.customer = %s
		""", (
			self.name,
			self.branch,
			self.from_date,
			self.to_date,
			self.from_date,
			self.to_date,
			self.from_date,
			self.to_date,
			self.customer
		), as_dict=1):

			doc = frappe.get_doc("Customer Selling Price", a.name)

			for b in doc.item_rates:
				key = (
					str(b.particular) + "/" +
					str(b.timber_type) + "/" +
					str(b.item_sub_group)
				)

				if key in item_list:
					if b.timber_type and b.item_sub_group:
						frappe.throw(
							"<b>{}/{}/{}</b> already defined for the same period in <b>{}</b>".format(
								b.particular,
								b.timber_type,
								b.item_sub_group,
								frappe.get_desk_link(self.doctype, a.name)
							)
						)
					else:
						frappe.throw(
							"<b>{}</b> already defined for Customer <b>{}</b> "
							"the same period in <b>{}</b>".format(
								b.particular,
								self.customer,
								frappe.get_desk_link(self.doctype, a.name)
							)
						)


@frappe.whitelist()
def get_customer_selling_rate(price_list, branch, item_code, transaction_date, customer):
	if not branch or not item_code or not transaction_date:
		frappe.throw("Select Item Code or Branch or Posting Date")

	# Item based rate
	rate = frappe.db.sql("""
		SELECT selling_price AS rate
		FROM `tabSelling Price Rate`
		WHERE parent = %s
		AND particular = %s
	""", (price_list, item_code), as_dict=1)

	# Timber based rate
	if not rate:
		species = frappe.db.get_value("Item", item_code, "species")
		if species:
			item_sub_group = frappe.db.get_value("Item", item_code, "item_sub_group")
			timber_class, timber_type = frappe.db.get_value(
				"Timber Species",
				species,
				["timber_class", "timber_type"]
			)

			rate = frappe.db.sql("""
				SELECT selling_price AS rate
				FROM `tabSelling Price Rate`
				WHERE parent = %s
				AND particular = %s
				AND timber_type = %s
				AND item_sub_group = %s
			""", (
				price_list,
				timber_class,
				timber_type,
				item_sub_group
			), as_dict=1)

	return rate and flt(rate[0].rate) or 0.0
