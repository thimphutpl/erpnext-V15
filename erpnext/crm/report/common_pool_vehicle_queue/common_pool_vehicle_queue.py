# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cint,add_days, cstr, flt, getdate, nowdate, rounded, date_diff
from erpnext.accounts.utils import get_child_cost_centers

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_columns(filters):
	columns = [
		{
			"fieldname": "vehicle",
			"label": "Vehicle",
			"fieldtype": "Link",
			"options": "Vehicle",
			"width": 120
		},
		{
			"fieldname": "vehicle_capacity",
			"label": "Vehicle Capacity",
			"fieldtype": "Link",
			"options": "Vehicle Capacity",
			"width": 120
		},
		{
			"fieldname": "load_status",
			"label": "Load Status",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "requesting_date_time",
			"label": "Requesting Date Time",
			"fieldtype": "Datetime",
			"width": 120
		},
		{
			"fieldname": "crm_branch",
			"label": "Branch",
			"fieldtype": "Link",
			"options": "Branch",
			"width": 100
		},
		{
			"fieldname": "token",
			"label": "Token",
			"fieldtype": "Int",
			"width": 100
		}
	]
	return columns

def get_data(filters):
    conditions = []
    values = []

    if filters.get("vehicle_capacity"):
        conditions.append("vehicle_capacity = %s")
        values.append(filters.get("vehicle_capacity"))

    if filters.get("from_date"):
        conditions.append("requesting_date_time >= %s")
        values.append(filters.get("from_date"))

    if filters.get("to_date"):
        conditions.append("requesting_date_time <= %s")
        values.append(filters.get("to_date"))

    condition_str = " AND ".join(conditions)
    if condition_str:
        condition_str = " AND " + condition_str

    query = f"""
        SELECT
            vehicle,
            vehicle_capacity,
            load_status,
            requesting_date_time,
            crm_branch,
            token
        FROM
            `tabLoad Request`
        WHERE
            load_status = 'Queued'
            AND crm_branch = 'Sha Sand and Stone Unit'
            {condition_str}
        ORDER BY
            requesting_date_time ASC,
            token ASC
    """

    return frappe.db.sql(query, values, as_dict=True)