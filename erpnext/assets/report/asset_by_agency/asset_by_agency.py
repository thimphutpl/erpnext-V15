# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = get_column(), get_data(filters)
	return columns, data

def get_column():
    columns = [
		("Agency") + ":Link/eNote:100",
		("Assets") + ":Data:200",
    ]
    return columns

def get_data(filters):
    conditions = get_condition(filters)
    return frappe.db.sql("""
        select company,count(name) from `tabAsset` where {conditions} group by company ;
		""".format(conditions=conditions))
   
    
    
def get_condition(filters):
    conds = "1=1 "
    if filters.company:
        conds += "and company='{}'".format(filters.company)
    return conds

