# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe import _, msgprint
from frappe.utils import get_link_to_form, nowdate, add_days, today

class AllotmentItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.crm.doctype.allotment_item_item.allotment_item_item import AllotmentItemItem
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		items: DF.Table[AllotmentItemItem]
		posting_date: DF.Date
		supplier: DF.Link
	# end: auto-generated types

	def on_submit(self):
		if any(row.select for row in self.items):
			self.create_purchase_order()
		else:
			frappe.throw("Select at least one item")

	def create_purchase_order(self):
		po = frappe.new_doc("Purchase Order")
		po.flags.ignore_permissions = 1 
		po.title = self.name
		po.branch = self.branch
		po.supplier = self.supplier
		po.schedule_date = self.posting_date
		po.allotment_item =  self.name
		for row in self.items:
			if row.select:
				po.append("items", {
					"qty": row.qty,
					"item_code": row.item_code,
					"item_name": row.item_name,
					"uom": "Unit",
					# "rate": row.rate,
					"c2_status": row.c2_status if row.c2_status else "",
					"order_type": "Confirm Order" if row.c2_status else "Stock Order"
				})
		po.insert(ignore_permissions=True)
		for row in self.items:
			if row.select:
				row.purchase_order = po.name
				if row.c2_status:
					doc = frappe.get_doc("C2 Status", row.c2_status)
					doc.purchase_order = po.name
					doc.allotment_item = self.name
					doc.save()
		self.save()
		# frappe.msgprint(
		# 	_(
		# 		"Purchase Order <b>{0}</b> created"
		# 	).format(po.name),
		# )
		frappe.msgprint(
			_("Purchase Order {0} created").format(
				get_link_to_form("Purchase Order", po.name)
			)
		)
				

@frappe.whitelist()
def get_details():
	entries = frappe.db.sql('''
		SELECT t1.customer_id, t1.customer_name, t1.phone_number, t1.id_card_no, 
		t2.item_code, t2.item_name, t1.name, t2.net_price, t2.quantity as qty, t2.price_costing,
		t2.tvo_numbervin_numbervi_number as tvo
		FROM `tabC2 Status` t1
		INNER JOIN `tabOrder Confirmation Details` t2
		ON t1.name = t2.parent
		AND t1.purchase_order IS NULL
		INNER JOIN `tabItem` t3
		ON t3.name = t2.item_code
		AND t3.include_in_allotment = 1
		WHERE t1.docstatus = 1 AND t1.purchase_order IS NULL order by t1.creation asc 
	''', as_dict=True)
	# frappe.throw(str(entries))
	if not entries:
		frappe.throw("No Records Found")
		
	return entries

# @frappe.whitelist()
# def create_sales_order(self):
# 	for row in self.items:
# 		if row.select:
# 			so = frappe.new_doc("Sales Order")
# 			so.flags.ignore_permissions = 1 
# 			so.title = self.name
# 			so.branch = self.branch
# 			so.customer = row.customer_id
# 			so.delivery_date = self.posting_date
# 			# so.allotment_item =  self.name
# 			so.append("items", {
# 				"qty": row.qty,
# 				"item_code": row.item_code,
# 				"item_name": row.item_name,
# 				"uom": "Unit",
# 				so.delivery_date: self.posting_date,

# 				# "rate": row.rate,
# 				"c2_status": row.c2_status,
# 				# "order_type": "Confirm Order" if row.customer_id else "Stock Order"
# 			})
# 			so.insert(ignore_permissions=True)
# 		# for row in self.items:
# 		# 	if row.select:
# 		# 		row.purchase_order = po.name
# 		# 		doc = frappe.get_doc("C2 Status", row.c2_status)
# 		# 		doc.purchase_order = po.name
# 		# 		doc.allotment_item = self.name
# 		# 		doc.save()
# 		# self.save()
# 		# frappe.msgprint(
# 		# 	_(
# 		# 		"Purchase Order <b>{0}</b> created"
# 		# 	).format(po.name),
# 		# )
# 		frappe.msgprint(
# 			_("Sales Order {0} created").format(
# 				get_link_to_form("Sales Order", so.name)
# 			)
# 		)

@frappe.whitelist()
def create_sales_order(docname):
	doc = frappe.get_doc("Allotment Item", docname)

	created_orders = []

	for row in doc.items:
		if row.select:
			so = frappe.new_doc("Sales Order")
			so.flags.ignore_permissions = 1

			so.title = doc.name
			so.branch = doc.branch
			so.customer = row.customer_id if row.customer_id else "STCBL"
			so.delivery_date = add_days(today(), 1)
			so.allotment_item = doc.name
			so.c2_status = row.c2_status

			# frappe.throw(str(add_days(today(), 1)))

			so.append("items", {
				"qty": row.qty,
				"item_code": row.item_code,
				"item_name": row.item_name,
				"uom": "Unit",
				"delivery_date": add_days(today(), 1),
				"c2_status": row.c2_status,
				"price_template": row.price_costing,
				"rate": row.rate,
				"qty": row.qty,
			})

			so.insert(ignore_permissions=True)
			row.sales_order = so.name
			row.save()
			if row.c2_status:
				c2 = frappe.get_doc("C2 Status", row.c2_status)
				c2.sales_order = so.name
				# c2.allotment_item = self.name
				c2.save()
			created_orders.append(so.name)
	return created_orders