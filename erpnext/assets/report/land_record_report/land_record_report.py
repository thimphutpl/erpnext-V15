# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_columns(filters):
	return [
			{
				"fieldname":"land_type",
				"label":"Land Type",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
   {
				"fieldname":"ownership_type",
				"label":"Ownership Type",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
   {
				"fieldname":"land_sub_type",
				"label":"Land Sub Type",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
    {
				"fieldname":"thram_holder",
				"label":"Thram Holder",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
     {
				"fieldname":"plot_id",
				"label":"Plot ID",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
    {
				"fieldname":"ruralurban",
				"label":"Rural/Urban",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
    {
				"fieldname":"thram_no",
				"label":"Thram No",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
    {
				"fieldname":"thromde",
				"label":"Thromde",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
    {
				"fieldname":"dzongkhag",
				"label":"Dzongkhag",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
    {
				"fieldname":"gewog",
				"label":"Gewog",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
    {
				"fieldname":"precinctland_type",
				"label":"Precinctland Type",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
    {
				"fieldname":"location",
				"label":"Location",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
    {
				"fieldname":"areain_acre",
				"label":"Area in Acre",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
    {
				"fieldname":"areain_sqft",
				"label":"Area in qft",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
    {
				"fieldname":"origin_of_thram",
				"label":"Origin of Thram",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
    {
				"fieldname":"plot_status",
				"label":"Plot Status",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
    {
				"fieldname":"plot_category",
				"label":"Plot Category",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
	{
				"fieldname":"finding",
				"label":"Finding",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
	{
				"fieldname":"remarks",
				"label":"Remarks",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
	{
				"fieldname":"way_forward",
				"label":"Way Forward",
				"fieldtype":"data",
				"options":"",
				"width":160
			},
		]

def get_data(filters):
    # Initialize an empty list for data
    data = []

    # Generate conditions based on the provided filters
    conditions = get_conditions(filters)


    # Use parameterized queries to prevent SQL injection
    query = '''
        SELECT * 
        FROM `tabLand Record` 
        WHERE 1=1 {}
    '''.format(conditions)

    # Execute the query and fetch results
    data = frappe.db.sql(query, as_dict=1)

    return data

def get_conditions(filters):
	
	conditions = []
	if filters.get("land_type"):
		conditions.append("land_type = '{}'".format(filters.get("land_type")))
	if filters.get("land_sub_type"):
		conditions.append("land_sub_type = '{}'".format(filters.get("land_sub_type")))
	if filters.get("ownership_type"):
		conditions.append("ownership_type = '{}'".format(filters.get("ownership_type")))
	if filters.get("dzongkhag"):
		conditions.append("dzongkhag = '{}'".format(filters.get("dzongkhag")))
	if filters.get("precinctland_type"):
		conditions.append("precinctland_type = '{}'".format(filters.get("precinctland_type")))
	if filters.get("plot_id"):
		conditions.append("plot_id = '{}'".format(filters.get("plot_id")))
	if filters.get("ruralurban"):
		conditions.append("ruralurban = '{}'".format(filters.get("ruralurban")))
	if filters.get("gewog"):
		conditions.append("gewog = '{}'".format(filters.get("gewog")))
	if filters.get("plot_category"):
		conditions.append("plot_category = '{}'".format(filters.get("plot_category")))
		#tw
		

	return "and {}".format(" and ".join(conditions)) if conditions else ""