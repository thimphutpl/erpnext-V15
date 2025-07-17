# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns=get_columns()
	data=get_data(filters)
	return columns, data
def get_columns():
	columns = [
		{
			"fieldname": "owned_by",
			"label": "Owned By",
			"fieldtype": "Data",
			"options": "Owned By",
			"width": 150
		},
		{
			"fieldname": "branch",
			"label": "Branch",
			"fieldtype": "Link",
			"options": "Branch",
			"width": 150
		},
		{
			"fieldname": "cost_center",
			"label": "Cost Center",
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 150
		},
		{
			"fieldname": "customer",
			"label": "Customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150
		},
		{
			"fieldname":"posting_date",
			"label": "Join In Date",
			"fieldtype": "Date",
			"options": "Posting Date",
			"width": 150
		},
		{
			"fieldname": "finish_date",
			"label": "Job Out Date",
			"fieldtype": "Date",
			"options": "Finish Date",
			"width":150
		},
		{
			"fieldname": "repair_type",
			"label": "Job Type",
			"fieldtype": "Data",
			"options": "Repair Type",
			"width": 150
		},
		{
			"fieldname": "name_of_the_job",
			"label": "Name of the job",
			"fieldtype": "Data",
			"options": "Name of the job",
			"width": 150
		},
		{
			"fieldname": "location",
			"label": "Location",
			"fieldtype": "Data",
			"options": "Location",
			"width": 150
		}
		
	]
	return columns
def get_data(filters=None):
	query = """
		SELECT
			fabb.owned_by,
			fabb.branch,
			fabb.cost_center,
			fabb.customer,
			fabb.posting_date,
			fabb.finish_date,
			fabb.repair_type,
			fabb.name_of_the_job,
			fabb.location


		FROM 
			`tabFabrication And Bailey Bridge` AS fabb
		WHERE 
			fabb.docstatus = 1
	"""
	if filters.get("branch"):
		query += " and fabb.branch = \'" + str(filters.branch) + "\'"
	if filters.get("cost_center"):
		query += " and fabb.cost_center = \'" + str(filters.cost_center) + "\'"
	if filters.get("company"):
		query += " and fabb.company = \'" + str(filters.company) + "\'"			

	return  frappe.db.sql(query)
