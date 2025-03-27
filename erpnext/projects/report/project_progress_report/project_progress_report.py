# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff

def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters=None):
	columns = []
	if not filters.get("cost_center") and not filters.get("project_definition") and not filters.get("project") and not filters.get("task"):
		columns = [
			{
			"fieldname": "cost_center",
			"label": "Cost Center",
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 150
			},
			{
			"fieldname": "start_date",
			"label": "Start Date",
			"fieldtype": "Date",
			"width": 120
			},
			{
			"fieldname": "end_date",
			"label": "End Date",
			"fieldtype": "Date",
			"width": 120
			},
			{
			"fieldname": "duration",
			"label": "Duration(Days)",
			"fieldtype": "Float",
			"width": 120
			},
			{
			"fieldname": "project_progress",
			"label": "Project Progress(%)",
			"fieldtype": "Float",
			"width": 120
			},
			{
			"fieldname": "site_progress",
			"label": "Site Progress(%)",
			"fieldtype": "Data",
			"width": 120
			},
			{
			"fieldname": "weightage",
			"label": "Weightage(%)",
			"fieldtype": "Float",
			"width": 120
			},
			# {
			# "fieldname": "type",
			# "label": "Income Type",
			# "fieldtype": "Data",
			# "width": 160
			# },
			# {
			# "fieldname": "basic",
			# "label": "Basic Salary",
			# "fieldtype": "Currency",
			# "width": 150
			# },
			# {
			# "fieldname": "others",
			# "label": "Allowances",
			# "fieldtype": "Currency",
			# "width": 120
			# },
			# {
			# "fieldname": "total",
			# "label": "Total Income",
			# "fieldtype": "Currency",
			# "width": 120
			# },
			# {
			# "fieldname": "pf",
			# "label": "PF",
			# "fieldtype": "Currency",
			# "width": 120
			# },
			# {
			# "fieldname": "gis",
			# "label": "GIS",
			# "fieldtype": "Currency",
			# "width": 120
			# },
			# {
			# "fieldname": "totalPfGis",
			# "label": "Total of PF & GIS",
			# "fieldtype": "Currency",
			# "width": 120
			# },
			# {
			# "fieldname": "taxable",
			# "label": "Taxable Income",
			# "fieldtype": "Currency",
			# "width": 120
			# },
			# {
			# "fieldname": "tds",
			# "label": "TDS Amount",
			# "fieldtype": "Currency",
			# "width": 120
			# },
			# {
			# "fieldname": "health",
			# "label": "Health",
			# "fieldtype": "Currency",
			# "width": 120
			# },
			# {
			# "fieldname": "receipt_number",
			# "label": "RRCO Receipt No.",
			# "fieldtype": "Data",
			# "width": 150
			# },
			# {
			# "fieldname": "receipt_date",
			# "label": "RRCO Receipt Date",
			# "fieldtype": "Date",
			# "width": 130
			# },
			# {
			# "fieldname": "posting_date",
			# "label": "Posting Date",
			# "fieldtype": "Date",
			# "width": 130
			# },
		]
	return columns

def get_data(filters=None):
	data = []
	if not filters.get("cost_center") and not filters.get("project_definition") and not filters.get("project") and not filters.get("task"):
		for cc in frappe.db.get_all("Cost Center", {"disabled": 0, "project_cost_center": 1}):
			start_date = None
			end_date = None
			duration = None
			start_dates = []
			end_dates = []
			for prj in frappe.db.get_all("Project Definition", {"cost_center": cc.name}, ["start_date", "end_date"]):
				if prj.start_date:
					start_dates.append(prj.start_date)
				if prj.end_date:
					end_dates.append(prj.end_date)
			if len(start_dates) > 0:
				start_date = min(start_dates)
			if len(end_dates) > 0:
				end_date = min(end_dates)
			if start_date and end_date:
				duration = date_diff(end_date, start_date)+1
			data.append({"cost_center": cc.name, "start_date": start_date, "end_date": end_date, "duration": duration})
	return data