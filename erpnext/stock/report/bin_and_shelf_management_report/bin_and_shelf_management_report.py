# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    columns = [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 180},
        {"label": "Branch", "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 180},
        {"label": "Bin", "fieldname": "bin", "fieldtype": "Data", "width": 140},
        {"label": "Shelf", "fieldname": "shelf", "fieldtype": "Data", "width": 180},
    ]

    conditions = ""

    if filters.get("item_code"):
        conditions += " AND it.item_code = %(item_code)s"

    if filters.get("branch"):
        conditions += " AND bs.branch = %(branch)s"

    data = frappe.db.sql(f"""
        SELECT
            it.item_code,
            bs.branch,
            bs.bin,
            bs.shelf
        FROM `tabItem` it
        LEFT JOIN `tabBin and Shelf Management` bs 
            ON bs.parent = it.name
        WHERE 1 = 1 {conditions}
    """, filters, as_dict=True)

    return columns, data
