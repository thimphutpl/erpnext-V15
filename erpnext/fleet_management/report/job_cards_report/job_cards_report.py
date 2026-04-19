# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns, data = get_columns(), get_data(filters)
    return columns, data

def get_columns():
    columns = [
        {
            "fieldname": "job_card_no",
            "label": _("Job Card Number"),
            "fieldtype": "Link",
            "options": "Job Cards",
            "width": 150
        },
        {
            "fieldname": "customer_name",
            "label": _("Customer Name"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "branch",
            "label": _("Branch"),
            "fieldtype": "Link",
            "options": "Branch",
            "width": 150
        },
        {
            "fieldname": "technician",
            "label": _("Technician"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "posting_date",
            "label": _("Job In Date"),
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "finish_date",
            "label": _("Job Out Date"),
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "total_amount",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "registration_no",
            "label": _("Registration No"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "repair_type",
            "label": _("Repair Type"),
            "fieldtype": "Data",
            "width": 150
        }
    ]
    return columns

def get_data(filters):
    conditions = get_conditions(filters)
    
    query = """
        SELECT 
            jc.name as job_card_no,
            jc.customer_name,
            jc.branch,
            jc.posting_date,
            jc.finish_date,
            jc.total_amount,
            jc.registration_no,
            jc.repair_type,
            GROUP_CONCAT(DISTINCT ma.employee_name SEPARATOR ', ') as technician
        FROM `tabJob Cards` jc
        LEFT JOIN `tabMechanic Assigned` ma ON ma.parent = jc.name
        WHERE jc.docstatus = 1
        {conditions}
        GROUP BY jc.name
        ORDER BY jc.posting_date DESC, jc.name DESC
    """.format(conditions=conditions)
    
    data = frappe.db.sql(query, filters, as_dict=1)
    return data

def get_conditions(filters):
    conditions = ""
    
    if not filters:
        return conditions
    
    if filters.get("from_date"):
        conditions += " AND jc.posting_date >= %(from_date)s"
    
    if filters.get("to_date"):
        conditions += " AND jc.posting_date <= %(to_date)s"
    
    if filters.get("branch"):
        conditions += " AND jc.branch = %(branch)s"
    
    if filters.get("customer"):
        conditions += " AND jc.customer = %(customer)s"
    
    if filters.get("job_card_no"):
        conditions += " AND jc.name LIKE %(job_card_no)s"
    
    if filters.get("registration_no"):
        conditions += " AND jc.registration_no LIKE %(registration_no)s"
    
    if filters.get("repair_type"):
        conditions += " AND jc.repair_type = %(repair_type)s"
    
    return conditions