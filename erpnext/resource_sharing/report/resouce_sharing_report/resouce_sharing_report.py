# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_columns(filters):
	return [
		{
			"fieldname": "resource",
			"label": _("Resource"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "from_date_time",
			"label": _("From Date Time"),
			"fieldtype": "Datetime",
			"width": 120
		},
		{
			"fieldname": "to_date_time",
			"label": _("To Date Time"),
			"fieldtype": "Datetime",
			"width": 120
		},
		{
			"fieldname": "requesting_by",
			"label": _("Requesting By"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "reason",
			"label": _("Reason"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "resource_type",
			"label": _("Resource Type"),
			"fieldtype": "Data",
			"width": 100
		},
		
		{
			"fieldname": "resource_name",
			"label": _("Resource Name"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "custodian",
			"label": _("Custodian"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "cost_center",
			"label": _("Cost Center"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "remarks",
			"label": _("Remarks"),
			"fieldtype": "Data",
			"width": 100
		}
	]

def get_conditions(filters):
    conditions = []

    if filters.get("to_date"):
        conditions.append("rn.to_date_time <= '{}'".format(filters.get("to_date")))
    if filters.get("from_date"):
        conditions.append("rn.from_date_time >= '{}'".format(filters.get("from_date")))
    if filters.get("resource_type"):
        conditions.append("rd.resource_type = '{}'".format(filters.get("resource_type")))
    if filters.get("resource"):
        conditions.append("rd.name = '{}'".format(filters.get("resource")))

    return " AND ".join(conditions)

def get_data(filters):
    conditions = get_conditions(filters)
    conditions_clause = f"WHERE {conditions}" if conditions else ""

    query = f'''
        SELECT
            rn.resource,
            rn.from_date_time,
            rn.to_date_time,
            rn.requesting_by,
            rn.reason,
            rd.resource_type,
            
            rd.resource_name,
            rd.custodian,
            rd.cost_center,
            rd.status,
            rd.remarks
        FROM
            `tabResource Booking` rn
        INNER JOIN
            `tabResource Directory` rd ON rn.resource = rd.name
        {conditions_clause}
    '''

    data = frappe.db.sql(query, as_dict=True)
    return data
