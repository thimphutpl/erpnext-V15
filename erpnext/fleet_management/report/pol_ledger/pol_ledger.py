# from __future__ import unicode_literals

# import frappe
# from frappe.utils import flt, get_datetime
# from operator import itemgetter

# # from erpnext.fleet_management.report.fleet_management_report import (
# #     get_pol_till,
# #     get_pol_consumed_till
# # )
# from erpnext.fleet_management.report.hsd_consumption_report.fleet_management_report import get_pol_till,get_pol_consumed_till

# def execute(filters=None):
#     columns = get_columns(filters)
#     data = get_data(filters)
#     return columns, data


# # ---------------------------
# # COLUMNS
# # ---------------------------
# def get_columns(filters):
#     columns = [
#         {"fieldname": "date_time", "label": "Date & Time", "fieldtype": "Datetime", "width": 140},
#         {"fieldname": "branch", "label": "Branch", "fieldtype": "Data", "width": 120},
#         {"fieldname": "equipment", "label": "Equipment", "fieldtype": "Link", "options": "Equipment", "width": 100},
#         {"fieldname": "equipment_no", "label": "Equipment No.", "fieldtype": "Data", "width": 100},
#         {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 130},
#         {"fieldname": "qty", "label": "Qty", "fieldtype": "Float", "width": 80},
#         {"fieldname": "reference", "label": "Reference", "fieldtype": "Data", "width": 100},
#         {"fieldname": "transaction_no", "label": "Transaction No.", "fieldtype": "Dynamic Link", "options": "reference", "width": 120},
#         {"fieldname": "purpose", "label": "Purpose", "fieldtype": "Data", "width": 90},
#         {"fieldname": "transaction_branch", "label": "Transaction Branch", "fieldtype": "Data", "width": 130},
#         {"fieldname": "direct_consumption", "label": "Direct Consumption", "fieldtype": "Data", "width": 50},
#     ]

#     if filters.get("tank_balance"):
#         columns.append({
#             "fieldname": "tank_balance",
#             "label": "Tanker Balance",
#             "fieldtype": "Float",
#             "width": 100
#         })
#     else:
#         columns.append({
#             "fieldname": "fuel_tank_balance",
#             "label": "Fuel Tank Balance",
#             "fieldtype": "Float",
#             "width": 100
#         })

#     return columns


# # ---------------------------
# # DATA
# # ---------------------------
# def get_data(filters=None):
#     filters = filters or {}
#     data = []

#     # ---------------------------
#     # SAFE CONDITIONS (NO .format)
#     # ---------------------------
#     conditions = ["docstatus = 1"]

#     if filters.get("from_date") and filters.get("to_date"):
#         conditions.append("posting_date BETWEEN %(from_date)s AND %(to_date)s")

#     if filters.get("branch"):
#         conditions.append("branch = %(branch)s")

#     if filters.get("equipment"):
#         conditions.append("equipment = %(equipment)s")

#     where_clause = " AND ".join(conditions)

#     # ---------------------------
#     # MAIN QUERY
#     # ---------------------------
#     pol_entries = frappe.db.sql(f"""
#         SELECT 
#             name, posting_date, posting_time,
#             branch, equipment, pol_type, qty,
#             type, reference_type, reference_name
#         FROM `tabPOL Entry`
#         WHERE {where_clause}
#         ORDER BY posting_date, posting_time
#     """, filters, as_dict=True)

#     if not pol_entries:
#         return []

#     # ---------------------------
#     # CACHES (IMPORTANT PERFORMANCE FIX)
#     # ---------------------------
#     item_cache = {}
#     equipment_cache = {}
#     branch_cache = {}
#     pol_cache = {}
#     consumed_cache = {}

#     def get_item(item_code):
#         if item_code not in item_cache:
#             item_cache[item_code] = frappe.db.get_value(
#                 "Item",
#                 item_code,
#                 ["item_name"],
#                 as_dict=True
#             )
#         return item_cache[item_code]

#     def get_equipment(equipment):
#         if equipment not in equipment_cache:
#             equipment_cache[equipment] = frappe.db.get_value(
#                 "Equipment",
#                 equipment,
#                 ["name", "registration_number", "equipment_type"],
#                 as_dict=True
#             )
#         return equipment_cache[equipment]

#     def get_branch(dt, dn):
#         key = (dt, dn)
#         if key not in branch_cache:
#             branch_cache[key] = frappe.db.get_value(dt, dn, "branch")
#         return branch_cache[key]

#     def cached_pol(mode, equipment, date, item):
#         key = (mode, equipment, date, item)
#         if key not in pol_cache:
#             pol_cache[key] = get_pol_till(mode, equipment, date, item)
#         return pol_cache[key]

#     def cached_consumed(equipment, date, time):
#         key = (equipment, date, time)
#         if key not in consumed_cache:
#             consumed_cache[key] = get_pol_consumed_till(equipment, date)
#         return consumed_cache[key]

#     # ---------------------------
#     # PROCESS ROWS
#     # ---------------------------
#     for entry in pol_entries:

#         item = get_item(entry.pol_type)
#         equipment = get_equipment(entry.equipment)

#         if not item or not equipment:
#             continue

#         ref_branch = get_branch(entry.reference_type, entry.reference_name)

#         direct_consumption = "Yes" if (
#             entry.reference_type == "POL Receive"
#             and frappe.get_value(entry.reference_type, entry.reference_name, "direct_consumption")
#         ) else "No"

#         received = cached_pol(
#             "Receive",
#             entry.equipment,
#             entry.posting_date,
#             entry.pol_type
#         )

#         consumed = cached_consumed(
#             entry.equipment,
#             entry.posting_date,
#             entry.posting_time
#         )

#         fuel_balance = flt(received) - flt(consumed)

#         tank_balance = 0
#         if equipment.get("equipment_type") == "Tanker":
#             stock = cached_pol("Stock", entry.equipment, entry.posting_date, entry.pol_type)
#             issued = cached_pol("Issue", entry.equipment, entry.posting_date, entry.pol_type)
#             tank_balance = flt(stock) - flt(issued)

#         row = [
#             get_datetime(f"{entry.posting_date} {entry.posting_time}"),
#             entry.branch,
#             entry.equipment,
#             equipment.get("registration_number"),
#             item.get("item_name"),
#             entry.qty,
#             entry.reference_type,
#             entry.reference_name,
#             entry.type,
#             ref_branch,
#             direct_consumption,
#         ]

#         if filters.get("tank_balance"):
#             row.append(tank_balance)
#         else:
#             row.append(fuel_balance)

#         data.append(row)

#     data.sort(key=itemgetter(0))
#     return data



# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr, get_datetime
from erpnext.fleet_management.fleet_utils import get_pol_till, get_pol_till,get_pol_consumed_till
from operator import itemgetter, attrgetter
import datetime

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_data(filters=None):
	data = []
	query = "select * from `tabPOL Entry` where docstatus = 1 "
	
	if filters.from_date and filters.to_date:
		query += " and posting_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"
	
	if filters.branch:
		query += " and branch = \'" + str(filters.branch) + "\'"

	if filters.equipment:
		query += " and equipment = \'" + str(filters.equipment) + "\'"

	query += " order by posting_date"
	# get_pol_till(purpose, equipment, date, pol_type=None)
	for eq in frappe.db.sql(query, as_dict=True):
		item = frappe.db.sql("select item_code, item_name, stock_uom from tabItem where `name`= \'" + str(eq.pol_type) + "\'", as_dict=True)
	
		branch = frappe.db.get_value(eq.reference_type, eq.reference_name, "branch")
		# dc = None
		# if eq.reference_type == "POL Recieve":
		# 	pol = frappe.get_doc(eq.reference_type, eq.reference)
		# 	if pol.direct_consumption:
		# 		dc = "Yes"
		dc = None
		if eq.reference_type == "POL Receive":
			pol = frappe.get_doc(eq.reference_type, eq.reference_name)
			dc = "Yes" if getattr(pol, "direct_consumption", 0) else "No"
	
#		get_pol_till(purpose, equipment, posting_date, pol_type=None, own_cc=None, posting_time="24:00"):
		received = get_pol_till("Receive", eq.equipment, eq.posting_date, eq.pol_type, posting_time=eq.posting_time )
		equipment = frappe.db.sql("select e.name, e.branch, e.equipment_type as equipment_type, et.is_container as is_container from tabEquipment e, `tabEquipment Type` et where e.equipment_type = et.name and e.name = \'" + str(eq.equipment) + "\'", as_dict=True)	
		if equipment[0]['is_container'] == 1:
			stock = get_pol_till("Stock", eq.equipment, eq.posting_date, eq.pol_type, posting_time=eq.posting_time)
			issued = get_pol_till("Issue", eq.equipment, eq.posting_date, eq.pol_type, posting_time=eq.posting_time)
			balance = flt(stock) - flt(issued)
		else:
			balance = 0
		if eq.type == "Issue":
			trans_qty = eq.qty*-1
		else:
			trans_qty = eq.qty

		row = frappe._dict({
			"posting_date":get_datetime(str(eq.posting_date) + " " + str(eq.posting_time)), 
			"branch":eq.branch, 
			"equipment":eq.equipment, 
			"item_name":item[0]['item_name'], 
			"trans_qty":trans_qty, 
			"balance":balance, 
			"type":eq.type, 
			"reference_type":eq.reference_type,
			"reference" :eq.reference_name, 
			"direct_comsumption": dc})
		data.append(row)
		
	return data

def get_columns():
	return [
		{"fieldname":"posting_date","fieldtype":"Datetime","width":150,"label":"Posting Date"},
		{"fieldname":"branch","fieldtype":"Link","width":130,"label":"Branch", "options":"Branch"},
		{"fieldname":"equipment","fieldtype":"Link","width":120,"label":"Equipment", "options":"Equipment"},
		{"fieldname":"item_name","fieldtype":"Data","width":100,"label":"Item Name"},
		{"fieldname":"trans_qty","fieldtype":"Float","width":100,"label":"Qty"},
		{"fieldname":"balance","fieldtype":"Float","width":100,"label":"Tanker Balance"},
		{"fieldname":"type","fieldtype":"Data","width":100,"label":"Type"},
		{"fieldname":"reference_type","fieldtype":"Data","width":100,"label":"Reference Type"},
		{"fieldname":"reference","fieldtype":"Data","width":100,"label":"Reference"},
		{"fieldname":"direct_comsumption","fieldtype":"Data","width":100,"label":"Is Direct Consumption"},
	]
