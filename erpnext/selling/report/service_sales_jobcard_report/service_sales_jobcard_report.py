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
			"label": ("Name"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Service Sales Jobcard",
			"width": 160,
		},
		{
			"label": ("Customer"),
			"fieldname": "customer_id",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 160,
		},
		{
			"label": ("Address"),
			"fieldname": "address",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": ("Mobile Number"),
			"fieldname": "mobile_no",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": ("Contact Person"),
			"fieldname": "contact_person",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": ("End Date"),
			"fieldname": "end_date",
			"fieldtype": "Date",
			"width": 160,
		},
		{
			"label": ("Vehicle No"),
			"fieldname": "vehicle_number",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": ("VIN/Chassis No"),
			"fieldname": "chassis_number",
			"fieldtype": "Link",
			"options": "Serial No",
			"width": 160,
		},
		{
			"label": ("Service Type"),
			"fieldname": "jobcard_type",
			"fieldtype": "Link",
			"options": "Jobcard Type",
			"width": 160,
		},
		{
			"label": ("Jobcard Status"),
			"fieldname": "jobcard_status",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": ("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": ("Technician EMP ID"),
			"fieldname": "emp_id",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 160,
		},
		{
			"label": ("Technician Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": ("Designation"),
			"fieldname": "designation",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": ("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 160,
		},
		{
			"label": ("Item Name"),
			"fieldname": "service_item",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": ("Quantity"),
			"fieldname": "quantity",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": ("Rate"),
			"fieldname": "rate",
			"fieldtype": "Currency",
			"width": 160,
		},
		{
			"label": ("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 160,
		},
	]
	return columns

def get_data(filters):
	query = """
		SELECT 
			ssj.name, ssj.customer_id, ssj.address, ssj.mobile_no, ssj.contact_person, ssj.end_date, ssj.vehicle_number, ssj.chassis_number,
			ssj.jobcard_type, ssj.jobcard_status, sn.item_name, 
			jtd.emp_id, jtd.employee_name, jtd.designation,
			jsd.item_code, jsd.item_name as service_item, jsd.quantity, jsd.rate, jsd.amount
		FROM `tabService Sales Jobcard` AS ssj
		LEFT JOIN `tabSerial No` AS sn
		ON ssj.chassis_number = sn.name
		LEFT JOIN `tabJobcard Technican Details` AS jtd
		ON ssj.name = jtd.parent
		LEFT JOIN `tabJobcard Service Details` AS jsd
		ON ssj.name = jsd.parent
	"""
	
		# LEFT JOIN `tabC1 Status` AS c1
		# ON c0.customer_id = c1.customer_id
		# LEFT JOIN `tabCustomer Quotation Details` AS c1i
		# ON c1.name = c1i.parent
		# LEFT JOIN `tabC2 Status` AS c2
		# ON c0.customer_id = c2.customer_id
		# LEFT JOIN `tabOrder Confirmation Details` AS c2i
		# ON c2.name = c2i.parent

	# conditions = []

	# if filters.get("customer"):
	# 	conditions.append("c0.customer_id = %(customer)s")

	# if filters.get("item_code"):
	# 	conditions.append("c1i.item_code = %(item_code)s")
		
	# # if filters.get("item"):
	# #     conditions.append("pi.item = %(purchase_type)s")

	# if conditions:
	#     query += " AND " + " AND ".join(conditions)

	# # query += " ORDER BY p.posting_date DESC"

	return frappe.db.sql(query, filters, as_dict=True)
