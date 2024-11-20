# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data

def get_columns(filters):
	if filters.uinput == "Occupied":
		cols = [
			("Equipment") + ":Link/Equipment:120",
			("Customer") + ":Data:120",
			("From Date")+ ":Data:100",
			("To Date") + ":Data:120",
			("Place") + ":Data:120"
		]
	else:
		cols = [
			("Equipment") + ":Link/Equipment:120",
			("Equipment Number") + ":Data:120"
		]

	return cols

def get_data(filters):
	if filters.uinput == "Occupied":
		query ="""select e.name, (select h.customer FROM `tabEquipment Hiring Form` h WHERE h.name = r.ehf_name) AS customer, r.from_date, r.to_date, r.place FROM tabEquipment AS e,  `tabEquipment Reservation Entry` AS r WHERE e.name = r.equipment AND (r.to_date BETWEEN  \'%(to_date)s\'  AND  \'%(from_date)s\' OR r.from_date BETWEEN \'%(from_date)s\' AND \'%(to_date)s\')""" % {"from_date": str(filters.from_date), "to_date": str(filters.to_date)}

	if filters.uinput == "Free":
		query = "select e.name, e.equipment_number from tabEquipment e where NOT EXISTS (" + """select r.equipment FROM `tabEquipment Reservation Entry` AS r WHERE e.name=r.equipment and (r.to_date BETWEEN \'%(to_date)s\' AND \'%(from_date)s\' OR r.from_date BETWEEN \'%(from_date)s\' AND \'%(to_date)s\'))""" % {"from_date": str(filters.from_date), "to_date": str(filters.to_date)}

	if filters.get("branch"):
		query += " and e.branch = \'" + str(filters.branch) + "\'"

	if filters.get("equipment_type"):
		query += " and e.equipment_type = \'" + str(filters.equipment_type) + "\'"
	return frappe.db.sql(query)
