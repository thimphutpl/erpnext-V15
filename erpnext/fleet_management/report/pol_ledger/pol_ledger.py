# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr, get_datetime
from erpnext.fleet_management.fleet_utils import get_pol_till, get_pol_consumed_till
from operator import itemgetter, attrgetter
import datetime

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

# def get_data(filters=None):
# 	data = []
# 	query = "select pe.posting_date, pe.posting_time, pe.branch, pe.cost_center, pe.equipment, pe.equipment_category, pe.equipment_type, pe.pol_type, pe.qty, pe.reference_type, pe.reference_name, pe.type, pe.amount from `tabPOL Entry` pe, `tabEquipment Type`et where pe.docstatus = 1 and pe.equipment_type = et.name"
# 	# frappe.throw(str(query))
# 	if not filters.all_equipment:
# 		query += " and et.is_container = 1"
	
# 	if filters.from_date and filters.to_date:
# 		query += " and pe.posting_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"
	
# 	if filters.branch:
# 		query += " and pe.branch = \'" + str(filters.branch) + "\'"	

# 	if filters.equipment:
# 		query += " and pe.equipment = \'" + str(filters.equipment) + "\'"

# 	query += " order by pe.posting_date"

# 	for eq in frappe.db.sql(query, as_dict=True):
# 		item = frappe.db.sql("select item_code, item_name, stock_uom from tabItem where `name`= \'" + str(eq.pol_type) + "\'", as_dict=True)
		
# 		dc = None
# 		if eq.reference_type == "POL Receive":
# 			pol = frappe.get_doc(eq.reference_type, eq.reference_name)
# 			dc = "Yes" if getattr(pol, "direct_consumption", 0) else "No"
		
# 		received = issued = balance = 0
		
# 		if filters.all_equipment:
# 			# For all equipment - use equipment level calculations
# 			received = get_pol_till("Receive", eq.equipment, eq.posting_date, eq.pol_type, posting_time=eq.posting_time)
# 			issued = get_pol_till("Issue", eq.equipment, eq.posting_date, eq.pol_type, posting_time=eq.posting_time)
# 			balance = flt(received) - flt(issued)
# 		else:
# 			if equipment and equipment[0]['is_container'] == 1:
# 				stock = get_pol_till("Stock", eq.equipment, eq.posting_date, eq.pol_type, posting_time=eq.posting_time)
# 				issued = get_pol_till("Issue", eq.equipment, eq.posting_date, eq.pol_type, posting_time=eq.posting_time)
# 				balance = flt(stock) - flt(issued)
# 			else:
# 				balance = 0
# 			received = get_pol_till("Receive", eq.equipment, eq.posting_date, eq.pol_type, posting_time=eq.posting_time)
		
# 		if eq.type == "Issue":
# 			trans_qty = eq.qty * -1
# 		else:
# 			trans_qty = eq.qty

# 		row = [
# 			get_datetime(str(eq.posting_date) + " " + str(eq.posting_time)), 
# 			eq.branch, 
# 			eq.equipment, 
# 			item[0]['item_name'], 
# 			trans_qty, 
# 			balance, 
# 			eq.type, 
# 			eq.reference_type, 
# 			eq.reference_name, 
# 			dc
# 		]
# 		data.append(row)
		
# 	return data

def get_data(filters=None):
	data = []
	query = "select pe.posting_date, pe.posting_time, pe.branch, pe.cost_center, pe.equipment, pe.equipment_category, pe.equipment_type, pe.pol_type, pe.qty, pe.reference_type, pe.reference_name, pe.type, pe.amount from `tabPOL Entry` pe, `tabEquipment Type`et where pe.docstatus = 1 and pe.equipment_type = et.name"
	
	if not filters.all_equipment:
		query += " and et.is_container = 1"
	
	# When all_equipment is True, exclude Stock and Issue types
	if filters.all_equipment:
		query += " and pe.type not in ('Stock', 'Issue')"
	
	if filters.from_date and filters.to_date:
		query += " and pe.posting_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"
	
	if filters.branch:
		query += " and pe.branch = \'" + str(filters.branch) + "\'"	

	if filters.equipment:
		query += " and pe.equipment = \'" + str(filters.equipment) + "\'"

	query += " order by pe.posting_date"

	for eq in frappe.db.sql(query, as_dict=True):
		item = frappe.db.sql("select item_code, item_name, stock_uom from tabItem where `name`= \'" + str(eq.pol_type) + "\'", as_dict=True)
		
		dc = None
		if eq.reference_type == "POL Receive":
			pol = frappe.get_doc(eq.reference_type, eq.reference_name)
			dc = "Yes" if getattr(pol, "direct_consumption", 0) else "No"
		
		received = issued = balance = 0
		
		if filters.all_equipment:
			# For all equipment - use equipment level calculations
			received = get_pol_till("Receive", eq.equipment, eq.posting_date, eq.pol_type, posting_time=eq.posting_time)
			issued = get_pol_till("Issue", eq.equipment, eq.posting_date, eq.pol_type, posting_time=eq.posting_time)
			balance = flt(received) - flt(issued)
		else:
			equipment = frappe.db.sql("select e.name, e.branch, e.equipment_type as equipment_type, et.is_container as is_container from tabEquipment e, `tabEquipment Type` et where e.equipment_type = et.name and e.name = \'" + str(eq.equipment) + "\'", as_dict=True)
			
			if equipment and equipment[0]['is_container'] == 1:
				stock = get_pol_till("Stock", eq.equipment, eq.posting_date, eq.pol_type, posting_time=eq.posting_time)
				issued = get_pol_till("Issue", eq.equipment, eq.posting_date, eq.pol_type, posting_time=eq.posting_time)
				balance = flt(stock) - flt(issued)
			else:
				balance = 0
			received = get_pol_till("Receive", eq.equipment, eq.posting_date, eq.pol_type, posting_time=eq.posting_time)
		
		if eq.type == "Issue":
			trans_qty = eq.qty * -1
		else:
			trans_qty = eq.qty

		row = [
			get_datetime(str(eq.posting_date) + " " + str(eq.posting_time)), 
			eq.branch, 
			eq.equipment, 
			item[0]['item_name'], 
			trans_qty, 
			balance, 
			eq.type, 
			eq.reference_type, 
			eq.reference_name, 
			dc
		]
		data.append(row)
		
	return data

def get_columns(filters):
	cols = [
		{
			"fieldname": "posting_date",
			"fieldtype": "Datetime",
			"width": 150,
			"label": "Posting Date"
		},
		{
			"fieldname": "branch",
			"fieldtype": "Link",
			"width": 130,
			"label": "Branch",
			"options": "Branch"
		},
		{
			"fieldname": "equipment",
			"fieldtype": "Link",
			"width": 120,
			"label": "Equipment",
			"options": "Equipment"
		},
		{
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 100,
			"label": "Item Name"
		},
		{
			"fieldname": "trans_qty",
			"fieldtype": "Float",
			"width": 100,
			"label": "Qty"
		},
		{
			"fieldname": "balance",
			"fieldtype": "Float",
			"width": 100,
			"label": "Tanker Balance"
		},
		{
			"fieldname": "type",
			"fieldtype": "Data",
			"width": 100,
			"label": "Type"
		},
		{
			"fieldname": "reference_type",
			"fieldtype": "Data",
			"width": 100,
			"label": "Reference Type"
		},
		{
			"fieldname": "reference",
			"fieldtype": "Data",
			"width": 100,
			"label": "Reference"
		},
		{
			"fieldname": "direct_comsumption",
			"fieldtype": "Data",
			"width": 100,
			"label": "Is Direct Consumption"
		},
	]
	return cols