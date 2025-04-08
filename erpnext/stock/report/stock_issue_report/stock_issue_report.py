# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    """ Returns column definitions as a list of dictionaries. """
    return [
        {"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": "Material Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 110},
        {"label": "Material Name", "fieldname": "item_name", "fieldtype": "Data", "width": 120},
        {"label": "Material Group", "fieldname": "item_group", "fieldtype": "Data", "width": 120},
        {"label": "Material Sub Group", "fieldname": "item_sub_group", "fieldtype": "Data", "width": 150},
        {"label": "UoM", "fieldname": "uom", "fieldtype": "Data", "width": 50},
        {"label": "Qty", "fieldname": "qty", "fieldtype": "Float", "width": 50},
        {"label": "Valuation Rate", "fieldname": "valuation_rate", "fieldtype": "Currency", "width": 120},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 110},
        {
            "label": "Warehouse" if frappe.form_dict.get("purpose") == "Material Transfer" else "Cost Center",
            "fieldname": "warehouse" if frappe.form_dict.get("purpose") == "Material Transfer" else "cost_center",
            "fieldtype": "Link",
            "options": "Warehouse" if frappe.form_dict.get("purpose") == "Material Transfer" else "Cost Center",
            "width": 170
        },
        {"label": "Stock Entry", "fieldname": "stock_entry", "fieldtype": "Link", "options": "Stock Entry", "width": 120},
        {"label": "Stock Entry Title", "fieldname": "stock_entry_title", "fieldtype": "Data", "width": 190},
    ]

def get_data(filters):
    """ Returns stock issue or transfer data based on filters. """

    conditions = []
    params = {}

    if filters.purpose == "Material Transfer":
        purpose_condition = "se.purpose = 'Material Transfer'"
        extra_field = "sed.t_warehouse as warehouse"
    else:
        purpose_condition = "se.purpose = 'Material Issue'"
        extra_field = "sed.cost_center"

    query = f"""
        SELECT 
            se.posting_date, sed.item_code, sed.item_name, 
            i.item_group, i.item_sub_group, 
            sed.uom, sed.qty, sed.valuation_rate, sed.amount,
            {extra_field}, se.name as stock_entry, se.title as stock_entry_title
        FROM `tabStock Entry` se
        INNER JOIN `tabStock Entry Detail` sed ON se.name = sed.parent
        INNER JOIN `tabItem` i ON sed.item_code = i.item_code
        WHERE se.docstatus = 1 AND {purpose_condition}
    """

    # Apply filters dynamically
    if filters.get("warehouse"):
        conditions.append("sed.s_warehouse = %(warehouse)s")
        params["warehouse"] = filters.warehouse

    if filters.get("item_code"):
        conditions.append("sed.item_code = %(item_code)s")
        params["item_code"] = filters.item_code

    if filters.get("cost_center"):
        conditions.append("sed.cost_center = %(cost_center)s")
        params["cost_center"] = filters.cost_center.replace("'", "\\'")  # Escape single quotes

    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("se.posting_date BETWEEN %(from_date)s AND %(to_date)s")
        params["from_date"] = filters.from_date
        params["to_date"] = filters.to_date

    # Add conditions to query
    if conditions:
        query += " AND " + " AND ".join(conditions)

    return frappe.db.sql(query, params, as_dict=True)


	
