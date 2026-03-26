# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from erpnext.fleet_management.report.fleet_management_report import get_pol_between,get_pol_between_fuelbook

def execute(filters=None):
		columns = get_columns(filters)
		data = get_data(filters)
		return columns, data
def get_columns(filters):
	if filters.get("is_fuel_book"):
		return [
			{
				"label": ("Fuel Book"),
				"fieldname": "fuelbook",
				"fieldtype": "Link",
				"options": "Fuelbook",
				"width": 150,
			},
			{
				"label": ("Item Code"),
				"fieldname": "item_code",
				"fieldtype": "Data",
				"width": 100,
			},
			{
				"label": ("Item Name"),
				"fieldname": "item_name",
				"fieldtype": "Data",
				"width": 170,
			},
			{
				"label": ("Stock UoM"),
				"fieldname": "stock_uom",
				"fieldtype": "Link",
				"options": "Item",
				"width": 120,
			},
			{
				"label": ("Rate"),
				"fieldname": "rate",
				"fieldtype": "Float",
				"width": 120,
			},
			{
				"label": ("Amount"),
				"fieldname": "amount",
				"fieldtype": "Float",
				"width": 120,
			},
				{
				"label": ("Total Issue Quantity"),
				"fieldname": "issue_qty",
				"fieldtype": "Float",
				"width": 120,
			},
			{
				"label": ("Total Balance Quantity"),
				"fieldname": "fuel_qty",
				"fieldtype": "Float",
				"width": 120,
			},
		]

	else:
		# ---------------------------
		# ✅ Equipment Columns
		# ---------------------------
		return [
			{
				"label": ("Equipment"),
				"fieldname": "equipment",
				"fieldtype": "Link",
				"options": "Equipment",
				"width": 120,
			},
			{
				"label": ("Equipment No."),
				"fieldname": "registration_number",
				"fieldtype": "Data",
				"width": 120,
			},
			{
				"label": ("Item Code"),
				"fieldname": "item_code",
				"fieldtype": "Data",
				"width": 100,
			},
			{
				"label": ("Item Name"),
				"fieldname": "item_name",
				"fieldtype": "Data",
				"width": 170,
			},
			{
				"label": ("Stock UoM"),
				"fieldname": "stock_uom",
				"fieldtype": "Link",
				"options": "Item",
				"width": 120,
			},
			{
				"label": ("Rate"),
				"fieldname": "rate",
				"fieldtype": "Float",
				"width": 120,
			},
			{
				"label": ("Amount"),
				"fieldname": "amount",
				"fieldtype": "Float",
				"width": 120,
			},
			{
				"label": ("Total Issue Quantity"),
				"fieldname": "eq_issue_qty",
				"fieldtype": "Float",
				"width": 120,
			},
			{
				"label": ("Total Quantity"),
				"fieldname": "balance",
				"fieldtype": "Float",
				"width": 120,
			},
	
		]
def get_data(filters):
	data = []

	items = frappe.db.sql("""
		select item_code, item_name, stock_uom
		from tabItem
		where is_pol_item = 1
	""", as_dict=True)

	# ---------------------------
	# ✅ Fuelbook
	# ---------------------------
	if filters.get("is_fuel_book"):
		query = "SELECT name FROM `tabFuelbook` WHERE 1 AND type='General Pol'"

		for fb in frappe.db.sql(query, as_dict=True):
			for item in items:
				own_cc = 1 if filters.get("own_cc") else 0

				fuel_qty = get_pol_between_fuelbook(
					"Issue",
					"General Pol",
					fb.name,
					filters.from_date,
					filters.to_date,
					own_cc
				)

				# If balance is None, make it 0
				if fuel_qty is None:
					fuel_qty = 0

				# Append all Fuelbooks, even if balance is 0
				data.append([
					fb.name,
					item.item_code,
					item.item_name,
					item.stock_uom,

					fuel_qty["rate"],
					fuel_qty["amount"],
					fuel_qty["issue_qty"],  # Total Issue Quantity
					fuel_qty["fuel_qty"]
				
			 
				])

	# ---------------------------
	# ✅ Equipment
	# ---------------------------
	else:
		query = "SELECT name, registration_number FROM `tabEquipment` WHERE 1"

		if filters.get("branch"):
			query += " AND branch = '" + str(filters.branch) + "'"

		for eq in frappe.db.sql(query, as_dict=True):
			for item in items:
				own_cc = 1 if filters.get("own_cc") else 0

				balance = get_pol_between(
					"Issue",
					eq.name,
					filters.from_date,
					filters.to_date,
					own_cc
				)

				if balance is None:
					balance = 0

				# Optionally, only append if balance > 0 for equipment
			
				data.append([
					eq.name,
					eq.registration_number,
					item.item_code,
					item.item_name,
					item.stock_uom,
					balance["rate"],
					balance["amount"],
					balance["eq_issue_qty"],  # Total Issue Quantity
					balance["balance"] 
				])

	return data