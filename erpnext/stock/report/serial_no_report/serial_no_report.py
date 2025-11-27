# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# # import frappe

# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Serial No", "fieldname": "serial_no", "fieldtype": "Link", "options": "Serial No", "width": 150},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 130},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 180},
        {"label": "Item Group", "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 130},

        # Purchase
        {"label": "Purchase Doc Type", "fieldname": "purchase_doctype", "fieldtype": "Data", "width": 120},
        {"label": "Purchase Doc No", "fieldname": "purchase_docno", "fieldtype": "Dynamic Link",
         "options": "purchase_doctype", "width": 160},
        {"label": "Purchase Date", "fieldname": "purchase_date", "fieldtype": "Date", "width": 110},
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 150},
		{"label": "Incoming Rate", "fieldname": "purchase_rate", "fieldtype": "Currency", "width": 150},

        # Delivery
        {"label": "Delivery Doc Type", "fieldname": "delivery_doctype", "fieldtype": "Data", "width": 120},
        {"label": "Delivery Doc No", "fieldname": "delivery_docno", "fieldtype": "Dynamic Link",
         "options": "delivery_doctype", "width": 160},
        {"label": "Delivery Date", "fieldname": "delivery_date", "fieldtype": "Date", "width": 110},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": "Outgoing Rate", "fieldname": "outgoing_rate", "fieldtype": "Currency", "width": 150},

        {"label": "Warranty Expiry", "fieldname": "warranty_expiry_date", "fieldtype": "Date", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 110},
        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 140},
    ]


def get_data(filters):
    conditions = []
    values = {}

    if filters.get("item_code"):
        conditions.append("sn.item_code = %(item_code)s")
        values["item_code"] = filters.get("item_code")

    if filters.get("item_group"):
        conditions.append("sn.item_group = %(item_group)s")
        values["item_group"] = filters.get("item_group")

    if filters.get("status"):
        conditions.append("sn.status = %(status)s")
        values["status"] = filters.get("status")

    # Default status filter if none selected
    else:
        conditions.append("sn.status IN ('Active', 'Delivered')")

    where_clause = "WHERE " + " AND ".join(conditions)

    sql = f"""
        SELECT
            sn.name AS serial_no,
            sn.item_code,
            sn.item_name,
            sn.item_group,

            sn.purchase_document_type AS purchase_doctype,
            sn.purchase_document_no AS purchase_docno,
            sn.purchase_date,
            sn.supplier,
            sn.purchase_rate,

            sn.delivery_document_type AS delivery_doctype,
            sn.delivery_document_no AS delivery_docno,
            sn.delivery_date,
            sn.customer,
            sn.outgoing_rate,

            sn.warranty_expiry_date,
            sn.status,
            sn.warehouse

        FROM `tabSerial No` sn
        {where_clause}
        ORDER BY sn.name ASC
    """
    return frappe.db.sql(sql, values, as_dict=True)


