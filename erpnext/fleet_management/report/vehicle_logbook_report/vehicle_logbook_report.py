# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# from __future__ import unicode_literals
# import frappe
# from frappe import _
# from frappe.utils.data import get_first_day, get_last_day, add_days
# from frappe.utils import flt, getdate, formatdate, cstr
# from erpnext.fleet_management.report.fleet_management_report import get_km_till, get_hour_till, get_pol_till, \
# 	get_pol_between, get_pol_consumed_till

# def execute(filters=None):
# 	columns = get_columns()
# 	query = construct_query(filters)
# 	data = get_data(query, filters)

# 	return columns, data

# def get_data(query, filters=None):
# 	data = []
# 	datas = frappe.db.sql(query, as_dict=True);
# 	for d in datas:
# 		row = [d.branch, d.registration_number, d.total_work_time, d.project, d.work_time, d.operator, d.operator_salary, d.hsd_rate, d.Consumption, d.hire_charge_amount,]
# 		data.append(row);
# 	return data

# def construct_query(filters):
# 	query = """select v.branch, v.registration_number, v.total_work_time, vl.project, vl.work_time, vl.operator, vl.operator_salary, vl.hsd_rate, v.consumption, v.hire_charge_amount
# 		from `tabVehicle Logbook` v, `tabVehicle Log` vl 
# 		"""

# 	if filters.get("branch"):
# 		query += " and v.branch = \'" + str(filters.branch) + "\'"

# 	if filters.get("from_date") and filters.get("to_date"):
# 		query += " and ('{0}' >= ifnull(v.from_date, curdate()) and '{1}' <= ifnull(v.to_date, curdate()))".format(filters.to_date, filters.from_date)

# 	return query

# def get_columns():
# 	cols = [
# 		("Branch") + ":Link/Branch:120",
# 		("Registration Number") + ":data:120",
# 		("Total Work Times (Hours).") + ":data:120",
# 		# vehicle log child table vlogs
# 		("Project")+"Link/Project:120",
# 		("Work Times (Hours)")+":float:100", 
# 		("Operator")+":Link/Operator:100",
# 		("Operator Salary")+":Currency:100",
# 		("HSD Rate")+":float:100",
# 		("HSD Consumption(L)")+":float:110",
# 		("Hire Charge Amount")+":float:100",

# 	]
# 	return cols



# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate

def execute(filters=None):
    columns = get_columns()
    query = construct_query(filters)
    data = get_data(query, filters)
    return columns, data

def get_data(query, filters=None):
    data = []
    datas = frappe.db.sql(query, filters, as_dict=True)
    for d in datas:
        row = [
            d.branch,
            d.registration_number,
            d.total_work_time,
            d.project,
            d.work_time,
            d.operator,
            d.driver_name,
            d.operator_salary,
            d.hsd_rate,
            d.consumption,
            d.hire_charge_amount,
            d.total_amount
        ]
        data.append(row)
    return data

def construct_query(filters):
    query = """
        SELECT
            v.branch,
            v.registration_number,
            v.total_work_time,
            vl.project,
            vl.work_time,
            vl.operator,
            vl.driver_name,
            vl.operator_salary,
            vl.hsd_rate,
            v.consumption,
            v.hire_charge_amount,
            v.total_amount
        FROM
            `tabVehicle Logbook` v
        INNER JOIN
            `tabVehicle Log` vl ON v.name = vl.parent
        WHERE
            1=1
    """

    if filters.get("branch"):
        query += " AND v.branch = %(branch)s"

    if filters.get("project"):
        query += " AND vl.project = %(project)s"

    if filters.get("registration_number"):
        query += " AND v.registration_number = %(registration_number)s"

    if filters.get("from_date") and filters.get("to_date"):
        query += """
            AND v.from_date >= %(from_date)s
            AND v.to_date <= %(to_date)s
        """

    return query

def get_columns():
    cols = [
        ("Branch") + ":Link/Branch:120",
        ("Registration Number") + ":Data:120",
        ("Total Work Times (Hours)") + ":Float:120",
        ("Project") + ":Link/Project:120",
        ("Work Times (Hours)") + ":Float:100",
        ("Operator") + ":Link/Operator:100",
        ("Operator Name") + ":Data:100",
        ("Operator Salary") + ":Currency:100",
        ("HSD Rate") + ":Float:100",
        ("HSD Consumption (L)") + ":Float:110",
        ("Hire Charge Amount") + ":Currency:100",
        ("Total Amount") + ":Float:100",
    ]
    return cols