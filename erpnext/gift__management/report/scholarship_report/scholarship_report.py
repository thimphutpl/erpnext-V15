# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data
# scholarship_report.py (script report)

import frappe
from frappe.utils import nowdate

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "name", "label": "ID", "fieldtype": "Link", "options": "Scholarship"},
        {"fieldname": "batch", "label": "Batch", "fieldtype": "Data"},
        {"fieldname": "country", "label": "Country", "fieldtype": "Data"},
        {"fieldname": "name1", "label": "Student Name", "fieldtype": "Data"},
        {"fieldname": "cid_number", "label": "CID Number", "fieldtype": "Data"},
        {"fieldname": "permanent_address", "label": "Permanent Address", "fieldtype": "Data"},
        {"fieldname": "contact_number", "label": "Contact Number", "fieldtype": "Data"},
        {"fieldname": "email_address", "label": "Email Address", "fieldtype": "Data"},
        {"fieldname": "college", "label": "College", "fieldtype": "Data"},
        {"fieldname": "course", "label": "Course", "fieldtype": "Data"},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data"},
        {"fieldname": "start_date", "label": "Start Date", "fieldtype": "Date"},
        {"fieldname": "end_date", "label": "End Date", "fieldtype": "Date"},
    ]

def get_data(filters):
    today = nowdate()
    return frappe.db.sql("""
        SELECT
            name, batch, country, name1, cid_number, permanent_address, contact_number, email_address, college, course, status, start_date, end_date
        FROM
            `tabScholarship`
        WHERE
            docstatus = 1
    """, as_dict=1)
