# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe.utils import get_first_day, get_last_day
from datetime import datetime

def execute(filters=None):
    # Define the columns for the report
    columns = [
        {"label": "Month", "fieldname": "month", "fieldtype": "Data", "width": 150},
        {"label": "Price List Count", "fieldname": "price_list_count", "fieldtype": "Int", "width": 150},
    ]

    # Fetch the data for the report
    data = get_cop_trend_data(filters)

    # Prepare chart for the trendline
    chart = {
        "data": {
            "labels": [row["month"] for row in data],
            "datasets": [
                {
                    "name": "Price List Trend",
                    "values": [row["price_list_count"] for row in data],
                }
            ],
        },
        "type": "line",  # Trendline graph
    }

    return columns, data, None, chart


def get_cop_trend_data(filters):
    if not filters or not filters.get("item_code"):
        frappe.throw(("Please select an Item Code"))

    # Default year filter to the current year
    year = filters.get("year") or datetime.now().year

    # Initialize data for each month
    data = []
    for month in range(1, 13):
        start_date = get_first_day(datetime(year, month, 1))
        end_date = get_last_day(start_date)

        # Query to count unique price lists for the month
        price_list_count = frappe.db.sql(
            """
            SELECT COUNT(DISTINCT price_list) AS count
            FROM `tabItem Price`
            WHERE item_code = %s
            AND (valid_from IS NULL OR valid_from <= %s)
            AND (valid_upto IS NULL OR valid_upto >= %s)
            """,
            (filters["item_code"], end_date, start_date),
        )[0][0] or 0

        # Append month and price list count to data
        data.append({
            "month": start_date.strftime("%B %Y"),
            "price_list_count": price_list_count,
        })

    return data

