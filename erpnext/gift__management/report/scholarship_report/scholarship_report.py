# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

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
    conditions = []
    
    # Apply filters dynamically
    if filters.get("college"):
        conditions.append("college = %(college)s")
    if filters.get("cid_number"):
        conditions.append("cid_number = %(cid_number)s")
    if filters.get("name1"):
        conditions.append("name1 = %(name1)s")
    if filters.get("country"):
        conditions.append("country = %(country)s")
    if filters.get("status"):
        conditions.append("status = %(status)s")    
    
    # Build the WHERE clause
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
        SELECT
            name, batch, country, name1, cid_number, permanent_address, contact_number, email_address, college, course, status, start_date, end_date
        FROM
            `tabScholarship`
        WHERE
            {where_clause}
    """
    
    # Execute the query with filters
    return frappe.db.sql(query, filters, as_dict=1)
