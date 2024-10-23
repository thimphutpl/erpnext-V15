# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {} 
        
    selected_report = filters.get('report_type', 'Inventory Report')

    if selected_report == "Inventory Report":
        columns, data = get_inventory_report_data()
    elif selected_report == "Inventory Summary":
        columns, data = get_inventory_summary_data()
    elif selected_report == "Non Moving Branch Wise":
        columns, data = get_non_moving_branch_data()
    else:
        columns, data = get_report_4_data()

    return columns, data

# Report 1 Data (Stock Ledger)
def get_inventory_report_data():
    columns = [
        {"fieldname": "item_code", "label": "Item Code", "fieldtype": "Data"},
        {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data"},
        {"fieldname": "opening", "label": "Opening", "fieldtype": "Float"},
        {"fieldname": "opening_receipt", "label": "Opening + Receipt", "fieldtype": "Float"},
        {"fieldname": "issue_value", "label": "Issue Value", "fieldtype": "Float"},
        {"fieldname": "valuation_rate", "label": "Valuation Rate", "fieldtype": "Float"},
        {"fieldname": "value", "label": "Value", "fieldtype": "Currency"},
        {"fieldname": "closing", "label": "Closing", "fieldtype": "Float"},
        {"fieldname": "consumption", "label": "Consumption", "fieldtype": "Float"},
        {"fieldname": "category", "label": "Category", "fieldtype": "Data"},
        {"fieldname": "movement", "label": "Nature of Movement", "fieldtype": "Data"},
    ]

    stock_entries = frappe.db.sql("""
        SELECT
            sle.item_code,
            i.item_name,
            sle.warehouse,
            SUM(sle.actual_qty) AS opening_qty,
            SUM(CASE WHEN sle.posting_date < CURDATE() THEN sle.actual_qty ELSE 0 END) AS opening_qty,
            SUM(CASE WHEN sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) AS in_qty,
            SUM(CASE WHEN sle.actual_qty < 0 THEN sle.actual_qty ELSE 0 END) AS out_qty,
            sle.valuation_rate,
            i.item_group AS category
        FROM `tabStock Ledger Entry` sle
        JOIN `tabItem` i ON i.name = sle.item_code
        WHERE sle.posting_date <= CURDATE()
        GROUP BY sle.item_code, sle.warehouse
    """, as_dict=True)

    total_opening_receipt = 0
    total_issue_value = 0
    total_valuation_rate = 0
    total_value = 0
    total_items = 0

    data = []
    for entry in stock_entries:
        opening = entry.opening_qty
        opening_receipt = entry.opening_qty + entry.in_qty
        issue_value = abs(entry.out_qty)
        # Calculate Closing
        closing = opening + (entry.in_qty - issue_value)
        consumption = (opening_receipt / issue_value) if issue_value else 0
        value = ((opening_receipt - issue_value) * entry.valuation_rate)
        
        # opening = entry.opening_qty
        # opening_receipt = opening + entry.in_qty
        # issue_value = entry.out_qty
        # # Calculate Closing
        # closing = opening + (entry.in_qty - issue_value)
        # consumption = (opening_receipt / issue_value) if issue_value else 0
        # value = ((opening_receipt - issue_value) * entry.valuation_rate)

        if consumption > 0.6:
            movement = "Fast Moving"
        elif 0 < consumption <= 0.6:
            movement = "Slow Moving"
        else:
            movement = "No Moving"

        data.append({
            "item_code":entry.item_code,
            "item_name":entry.item_name,
            "opening": opening,
            "opening_receipt": opening_receipt,
            "issue_value": issue_value,
            "valuation_rate": entry.valuation_rate,
            "value": value,
            "closing":closing,
            "consumption": consumption,
            "category": entry.category,
            "movement": movement,
        })

        total_opening_receipt += opening_receipt
        total_issue_value += issue_value
        total_valuation_rate += entry.valuation_rate
        total_value += value
        total_items += 1

    if total_items > 0:
        average_valuation_rate = total_valuation_rate / total_items
        
        data.append({
            "item_code": "",
            "item_name": "",
            "opening": "",
            "opening_receipt": total_opening_receipt,
            "issue_value": total_issue_value,
            "valuation_rate": average_valuation_rate, 
            "value": total_value,
            "closing": "",
            "consumption": "", 
            "movement": "",
            "category": "",
            "is_total_row": 1  # This flag will make the row bold
        })

    return columns, data

# Report 2
def get_inventory_summary_data():
    report_1_columns, report_1_data = get_inventory_report_data()

    summary = {
        "fast_moving": {"count": 0, "value": 0},
        "slow_moving": {"count": 0, "value": 0},
        "no_moving": {"count": 0, "value": 0},
    }
    total_items = 0
    total_value = 0

    for entry in report_1_data:
        total_items += 1
        total_value += entry["issue_value"]

        if entry["movement"] == "Fast Moving":
            summary["fast_moving"]["count"] += 1
            summary["fast_moving"]["value"] += entry["issue_value"]
        elif entry["movement"] == "Slow Moving":
            summary["slow_moving"]["count"] += 1
            summary["slow_moving"]["value"] += entry["issue_value"]
        else:
            summary["no_moving"]["count"] += 1
            summary["no_moving"]["value"] += entry["issue_value"]

    # Stock Balance should only include Fast and Slow Moving
    stock_balance_count = summary["fast_moving"]["count"] + summary["slow_moving"]["count"]
    stock_balance_value = summary["fast_moving"]["value"] + summary["slow_moving"]["value"]

    total_percent_items = 100
    total_percent_value = 100

    columns = [
        {"fieldname": "movement_type", "label": "Movement Type", "fieldtype": "Data"},
        {"fieldname": "num_items", "label": "Number of Items", "fieldtype": "Int"},
        {"fieldname": "item_percent", "label": "Item Percent", "fieldtype": "Percent"},
        {"fieldname": "total_value", "label": "Total Value", "fieldtype": "Float"},
        {"fieldname": "value_percent", "label": "Value Percent", "fieldtype": "Percent"}
    ]

    data = [
        {
            "movement_type": "Fast Moving",
            "num_items": summary["fast_moving"]["count"],
            "item_percent": (summary["fast_moving"]["count"] / total_items) * 100 if total_items else 0,
            "total_value": summary["fast_moving"]["value"],
            "value_percent": (summary["fast_moving"]["value"] / total_value) * 100 if total_value else 0
        },
        {
            "movement_type": "Slow Moving",
            "num_items": summary["slow_moving"]["count"],
            "item_percent": (summary["slow_moving"]["count"] / total_items) * 100 if total_items else 0,
            "total_value": summary["slow_moving"]["value"],
            "value_percent": (summary["slow_moving"]["value"] / total_value) * 100 if total_value else 0
        },
        {
            "movement_type": "No Moving",
            "num_items": summary["no_moving"]["count"],
            "item_percent": (summary["no_moving"]["count"] / total_items) * 100 if total_items else 0,
            "total_value": summary["no_moving"]["value"],
            "value_percent": (summary["no_moving"]["value"] / total_value) * 100 if total_value else 0
        },
        {
            "movement_type": "Stock Balance",
            "num_items": stock_balance_count,  # Sum of Fast and Slow Moving
            "total_value": stock_balance_value,  # Sum of Fast and Slow Moving
        },
        {
            "movement_type": "Total",
            "num_items": total_items,
            "item_percent": total_percent_items,
            "total_value": total_value,
            "value_percent": total_percent_value
        }
    ]

    return columns, data

# Report 3: Warehouse and Balance Value
def get_non_moving_branch_data():
    columns = [
        {"fieldname": "warehouse", "label": "Warehouse", "fieldtype": "Data"},
        {"fieldname": "balance_value", "label": "Value (Nu.)", "fieldtype": "Float"}
    ]

    warehouse_balances = frappe.db.sql("""
        SELECT
            sle.warehouse,
            SUM(sle.actual_qty * sle.valuation_rate) AS balance_value
        FROM `tabStock Ledger Entry` sle
        WHERE sle.posting_date <= CURDATE()
        GROUP BY sle.warehouse
    """, as_dict=True)

    data = []
    total_balance_value = 0

    for warehouse_entry in warehouse_balances:
        data.append({
            "warehouse": warehouse_entry.warehouse,
            "balance_value": warehouse_entry.balance_value
        })
        total_balance_value += warehouse_entry.balance_value

     # Add a row for the overall total
    data.append({
        "warehouse": "Overall Total",
        "balance_value": total_balance_value
    })    

    return columns, data


# Report 4 Data
def get_report_4_data():
    columns = [
        {"fieldname": "c1", "label": "C1", "fieldtype": "Data"},
        {"fieldname": "c2", "label": "C2", "fieldtype": "Data"},
        {"fieldname": "c3", "label": "C3", "fieldtype": "Data"},
        {"fieldname": "c4", "label": "C4", "fieldtype": "Data"}
    ]
    data = [
        {"c1": "C1 Data", "c2": "C2 Data", "c3": "C3 Data", "c4": "C4 Data"}
    ]
    return columns, data