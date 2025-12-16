# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data


def get_columns(filters):
	columns = [
		{
			"label": ("Price Costing Name"),
			"fieldname": "price_costing_name",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": ("Purchase Type"),
			"fieldname": "purchase_type",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": ("Item Code"),
			"fieldname": "item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 160,
		},
		{
			"label": ("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": ("Selling Price"),
			"fieldname": "selling_price",
			"fieldtype": "Currency",
			"width": 160,
		},
	]
	return columns

def get_data(filters):
	query = """
		SELECT 
			p.price_costing_name, p.purchase_type, pi.item, pi.item_name, pi.selling_price
		FROM `tabPrice Costing` AS p 
		JOIN `tabPrice Costing Item` as pi
		ON pi.parent = p.name
		WHERE p.docstatus = 1
	"""

	conditions = []

	if filters.get("price_costing_name"):
		conditions.append("p.price_costing_name LIKE %(price_costing_name)s")
		filters["price_costing_name"] = f"%{filters['price_costing_name']}%"

	if filters.get("purchase_type"):
		conditions.append("p.purchase_type LIKE %(purchase_type)s")
		filters["purchase_type"] = f"%{filters['purchase_type']}%"
		
	if filters.get("item"):
	    conditions.append("pi.item = %(purchase_type)s")

	if conditions:
	    query += " AND " + " AND ".join(conditions)

	query += " ORDER BY p.posting_date DESC"

	return frappe.db.sql(query, filters, as_dict=True)
