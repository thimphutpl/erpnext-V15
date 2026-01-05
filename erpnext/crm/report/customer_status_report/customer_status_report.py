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
			"label": ("Customer"),
			"fieldname": "customer_id",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 160,
		},
		{
			"label": ("C0 Name"),
			"fieldname": "c0_name",
			"fieldtype": "Link",
			"options": "C0 Status",
			"width": 160,
		},
		{
			"label": ("Responsible Branch"),
			"fieldname": "responsible_branch",
			"fieldtype": "Link",
			"options": "Branch",
			"width": 160,
		},
		{
			"label": ("Phone Number"),
			"fieldname": "phone_number",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": ("Email"),
			"fieldname": "email_id",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": ("C0 Inquiry"),
			"fieldname": "inquiry",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": ("C0 Repsonse"),
			"fieldname": "response",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": ("C1 Name"),
			"fieldname": "c1_name",
			"fieldtype": "Link",
			"options": "C1 Status",
			"width": 160,
		},
		{
			"label": ("C1 Item Code"),
			"fieldname": "c1_item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 160,
		},
		{
			"label": ("C1 Item Name"),
			"fieldname": "c1_item_name",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": ("C1 Quantity"),
			"fieldname": "c1_quantity",
			"fieldtype": "Currency",
			"width": 160,
		},
		{
			"label": ("C1 Gross Price"),
			"fieldname": "c1_amount",
			"fieldtype": "Currency",
			"width": 160,
		},
		{
			"label": ("C1 Discount Amount"),
			"fieldname": "c1_discount_amount",
			"fieldtype": "Currency",
			"width": 160,
		},
		{
			"label": ("C1 Net Price"),
			"fieldname": "c1_net_price",
			"fieldtype": "Currency",
			"width": 160,
		},
		{
			"label": ("C2 Name"),
			"fieldname": "c2_name",
			"fieldtype": "Link",
			"options": "C2 Status",
			"width": 160,
		},
		{
			"label": ("C2 Item Code"),
			"fieldname": "c2_item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 160,
		},
		{
			"label": ("C2 Quantity"),
			"fieldname": "c2_quantity",
			"fieldtype": "Currency",
			"width": 160,
		},
		{
			"label": ("C2 Gross Price"),
			"fieldname": "c2_gross_price",
			"fieldtype": "Currency",
			"width": 160,
		},
		{
			"label": ("C2 Discount Amount"),
			"fieldname": "c2_discount_amount",
			"fieldtype": "Currency",
			"width": 160,
		},
		{
			"label": ("C2 Net Price"),
			"fieldname": "c2_net_price",
			"fieldtype": "Currency",
			"width": 160,
		},
		{
			"label": ("C2 Advances Paid"),
			"fieldname": "advances_paid",
			"fieldtype": "Currency",
			"width": 160,
		},
		{
			"label": ("C2 Advance Remarks"),
			"fieldname": "advance__remarks",
			"fieldtype": "Data",
			"width": 160,
		},
	]
	return columns

def get_data(filters):
	query = """
		SELECT 
			c0.name as c0_name, c0.customer_id, c0.responsible_branch, c0.phone_number, c0.email_id, c0.inquiry, c0.response,
			c1.name as c1_name, c1i.item_code as c1_item_code, c1i.item_name as c1_item_name, c1i.quantity as c1_quantity, c1i.amount as c1_amount, c1i.discount_amount as c1_discount_amount, c1i.net_price as c1_net_price,
			c2.name as c2_name, c2i.item_code as c2_item_code, c2i.quantity as c2_quantity, c2i.gross_price as c2_gross_price, c2i.discount_amount as c2_discount_amount, c2i.net_price as c2_net_price, c2i.advances_paid, c2i.advance__remarks
		FROM `tabC0 Status` AS c0 
		LEFT JOIN `tabC1 Status` AS c1
		ON c0.customer_id = c1.customer_id
		LEFT JOIN `tabCustomer Quotation Details` AS c1i
		ON c1.name = c1i.parent
		LEFT JOIN `tabC2 Status` AS c2
		ON c0.customer_id = c2.customer_id
		LEFT JOIN `tabOrder Confirmation Details` AS c2i
		ON c2.name = c2i.parent
		WHERE c0.docstatus = 1 AND c1.docstatus = 1 AND c2.docstatus = 1
	"""

	conditions = []

	if filters.get("customer"):
		conditions.append("c0.customer_id = %(customer)s")

	if filters.get("item_code"):
		conditions.append("c1i.item_code = %(item_code)s")
		
	# if filters.get("item"):
	#     conditions.append("pi.item = %(purchase_type)s")

	if conditions:
	    query += " AND " + " AND ".join(conditions)

	# query += " ORDER BY p.posting_date DESC"

	return frappe.db.sql(query, filters, as_dict=True)
