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
		from erpnext.production.doctype.customer_price_branch.customer_price_branch import CustomerPriceBranch
		from erpnext.production.doctype.selling_price_rate.selling_price_rate import SellingPriceRate
		from frappe.types import DF

		branch: DF.Table[CustomerPriceBranch]
		company: DF.Link
		customer: DF.Link
		from_date: DF.Date
		item_rates: DF.Table[SellingPriceRate]
		to_date: DF.Date
	# end: auto-generated types

	def validate(self):
		self.check_sp_rate()
		

	def on_update(self):
		self.check_duplicate_entries()
		#self.check_duplicate_settings()


	def check_sp_rate(self):
		
		for a in self.item_rates:
			if not flt(a.selling_price) > 0:
				frappe.throw(
					"Selling Rate should be greater than 0 for <b>{}</b>".format(a.particular)
				)

			if a.price_based_on == "Item":
				a.item_name = frappe.db.get_value("Item", a.particular, "item_name")
				a.item_sub_group = None
			else:
				a.item_name = None
	def check_duplicate_entries(self):
		#frappe.throw("hi")
		branches = frappe.db.sql("select branch, count(branch) as num from `tabCustomer Price Branch` where parent = %s group by branch having num > 1", self.name, as_dict=1)
		for a in branches:
			
			#frappe.msgprint(str(a))
			frappe.throw("Branch <b>" + str(a.branch) + "</b> has been defined more than once")
			

		Items = frappe.db.sql("select particular, count(particular) as num from `tabSelling Price Rate` where parent = %s group by particular having num > 1", self.name, as_dict=1)
		for a in Items:
			#frappe.msgprint(str(a))
			frappe.throw("Item <b>" + str(a.particular) + "</b> has been defined more than once")

		
	# def check_duplicate_settings(self):
    
	# 	item_list = []
	# 	for a in self.item_rates:
	# 		item_list.append(str(str(a.particular) + "/" + str(a.item_name)))
		
	# 	branch_list = [str(d.branch) for d in self.get("branch")]
		
		
	# 	branch_list.append("DUMMY")
		
		
	# 	branch_tuple = str(tuple(branch_list))
	# 	if len(branch_list) == 1:
	# 		branch_tuple = f"('{branch_list[0]}')"
		
		
	# 	sql_query = f"""
	# 		select a.branch, b.name 
	# 		from `tabCustomer Price Branch` a, `tabCustomer Selling Price` b 
	# 		where a.parent = b.name 
	# 		and b.name != %s 
	# 		and a.branch in {branch_tuple}
	# 		and (
	# 			%s between b.from_date and b.to_date 
	# 			or %s between b.from_date and b.to_date 
	# 			or (%s > b.from_date and %s < b.to_date) 
	# 			or (%s < b.from_date and %s > b.to_date)
	# 		)
	# 	"""
		
	# 	# Parameters for SQL query
	# 	params = (
	# 		self.name, 
	# 		self.from_date, 
	# 		self.to_date, 
	# 		self.from_date, 
	# 		self.to_date, 
	# 		self.from_date, 
	# 		self.to_date
	# 	)
		
		
	# 	duplicates = frappe.db.sql(sql_query, params, as_dict=1)
		
	# 	for duplicate in duplicates:
		
	# 		doc = frappe.get_doc("Customer Selling Price", duplicate.name)
	# 		for item_rate in doc.item_rates:
				
	# 			item_key = f"{item_rate.particular}/{item_rate.item_name}"
				
	# 			if item_key in item_list:
	# 				frappe.throw(f"""
	# 					<b>{item_rate.item_name}/{item_rate.particular}</b> 
	# 					already defined for the same period in 
	# 					<b>{frappe.get_desk_link('Customer Selling Price', duplicate.name)}</b>
	# 				""")
		
		
	# 	duplicates = frappe.db.sql(sql_query, params, as_dict=1)
		
	# 	for duplicate in duplicates:
		
	# 		doc = frappe.get_doc("Selling Price", duplicate.name)
	# 		for item_rate in doc.item_rates:
				
	# 			item_key = f"{item_rate.particular}/{item_rate.item_name}"
				
	# 			if item_key in item_list:
	# 				frappe.throw(f"""
	# 					<b>{item_rate.item_name}/{item_rate.particular}</b> 
	# 					already defined for the same period in 
	# 					<b>{frappe.get_desk_link('Selling Price', duplicate.name)}</b>
	# 				""")

	# def check_duplicate_settings(self):
	# 	#branches = frappe.db.sql("select branch, count(branch) as num from `tabCustomer Price Branch` where parent = %s group by branch having num > 1", self.name, as_dict=1)
	# 	#frappe.throw(str(branches))
	# 	item_list = []

	# 	# Duplicate check within same document
	# 	for a in self.item_rates:
	# 		rate_dtl = (
	# 			str(a.particular) + "/" +
	# 			str(a.timber_type) + "/" +
	# 			str(a.item_sub_group)
	# 		)

	# 		if rate_dtl in item_list:
	# 			frappe.throw(
	# 				"<b>{}, {}</b> already defined more than once".format(
	# 					a.particular, a.item_name
	# 				)
	# 			)

	# 		item_list.append(rate_dtl)

	# 	# Check customer + branch duplicate across documents
	# 	for a in frappe.db.sql("""
	# 		SELECT b.branch, b.name
	# 		FROM `tabCustomer Selling Price` b
	# 		WHERE b.name != %s
	# 		AND b.branch = %s
	# 		AND (
	# 			%s BETWEEN b.from_date AND b.to_date
	# 			OR %s BETWEEN b.from_date AND b.to_date
	# 			OR (%s > b.from_date AND %s < b.to_date)
	# 			OR (%s < b.from_date AND %s > b.to_date)
	# 		)
	# 		AND b.customer = %s
	# 	""", (
	# 		self.name,
	# 		self.branch,
	# 		self.from_date,
	# 		self.to_date,
	# 		self.from_date,
	# 		self.to_date,
	# 		self.from_date,
	# 		self.to_date,
	# 		self.customer
	# 	), as_dict=1):

	# 		doc = frappe.get_doc("Customer Selling Price", a.name)

	# 		for b in doc.item_rates:
	# 			key = (
	# 				str(b.particular) + "/" +
	# 				str(b.timber_type) + "/" +
	# 				str(b.item_sub_group)
	# 			)

	# 			if key in item_list:
	# 				if b.timber_type and b.item_sub_group:
	# 					frappe.throw(
	# 						"<b>{}/{}/{}</b> already defined for the same period in <b>{}</b>".format(
	# 							b.particular,
	# 							b.timber_type,
	# 							b.item_sub_group,
	# 							frappe.get_desk_link(self.doctype, a.name)
	# 						)
	# 					)
	# 				else:
	# 					frappe.throw(
	# 						"<b>{}</b> already defined for Customer <b>{}</b> "
	# 						"the same period in <b>{}</b>".format(
	# 							b.particular,
	# 							self.customer,
	# 							frappe.get_desk_link(self.doctype, a.name)
	# 						)
	# 					)


@frappe.whitelist()
def get_customer_selling_rate(price_list, branch, item_code, transaction_date, customer):
	#frappe.throw(str(price_list))
	if not branch or not item_code or not transaction_date:
		frappe.throw("Select Item Code or Branch or Posting Date")

	# Item based rate
	rate = frappe.db.sql("""
		SELECT selling_price AS rate
		FROM `tabSelling Price Rate`
		WHERE parent = %s
		AND particular = %s
	""", (price_list, item_code), as_dict=1)

	

	return rate and flt(rate[0].rate) or 0.0
