# from frappe.utils import flt, formatdate
# import frappe
# from frappe import _
# import calendar
# from erpnext.controllers.trends import get_period_date_ranges, get_period_month_ranges

# def execute(filters=None):
#     columns = get_columns(filters)
#     data = get_data(filters)
#     chart = get_chart_data(filters, data)
#     return columns, data, None, chart

# # -----------------------------
# # Columns
# # -----------------------------
# def get_columns(filters):
#     columns = [
#         {"fieldname": "cost_center", "label": "Cost Center", "fieldtype": "Link", "options": "Cost Center", "width": 180},
#         {"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer", "width": 180},
#         {"fieldname": "customer_type", "label": "Customer Type", "fieldtype": "Data", "width": 130},
#     ]

#     if filters.get("details") and filters.get("month") == "All":
#         for month in get_period_month_ranges("Monthly", filters["fiscal_year"]):
#             short = str(month[0])[0:3]
#             for suffix in ["Target", "Achieved", "Balance", "Percent"]:
#                 columns.append({
#                     "label": f"{short} {suffix}",
#                     "fieldtype": "Float",
#                     "width": 120
#                 })
#     elif filters.get("details") and filters.get("month") != "All":
#         short = filters.get("month")[0:3]
#         for suffix in ["Target", "Achieved", "Balance", "Percent"]:
#             columns.append({
#                 "label": f"{short} {suffix}",
#                 "fieldtype": "Float",
#                 "width": 120
#             })
#     else:
#         columns += [
#             {"label": "Total Target", "fieldtype": "Currency", "width": 160},
#             {"label": "Total Achieved", "fieldtype": "Currency", "width": 160},
#             {"label": "Total Balance", "fieldtype": "Currency", "width": 160},
#             {"label": "Total Achieved Percent %", "fieldtype": "Percent", "width": 160},
#         ]
#     return columns

# # -----------------------------
# # Data
# # -----------------------------
# def get_data(filters):
#     data = []

#     # Get default receivable account
#     default_receivable_account = frappe.get_value("Company", filters.get("company"), "default_receivable_account")
#     fiscal_year = filters.get("fiscal_year")
#     cost_center = filters.get("cost_center")

#     # Get fiscal year dates
#     fy = frappe.get_doc("Fiscal Year", fiscal_year)
#     year_start = fy.year_start_date
#     year_end = fy.year_end_date

#     # -----------------------------
#     # Fetch Target Records
#     # -----------------------------
#     conditions = "WHERE rt.docstatus = 1 AND rt.fiscal_year = %s"
#     values = [fiscal_year]

#     if cost_center:
#         conditions += " AND rt.cost_center = %s"
#         values.append(cost_center)

#     target_query = f"""
#         SELECT 
#             rt.cost_center,
#             rta.customer,
#             rta.customer_type,
#             rta.*
#         FROM `tabCustomer Revenue Target` rt
#         INNER JOIN `tabRevenue Target Customer` rta
#             ON rta.parent = rt.name
#         {conditions}
#     """

#     records = frappe.db.sql(target_query, tuple(values), as_dict=True)
#     if not records:
#         return data

#     # -----------------------------
#     # Fetch GL Entries (Single Query)
#     # -----------------------------
#     gl_query = """
#         SELECT
#             party,
#             account,
#             MONTH(posting_date) as month,
#             SUM(debit - credit) as amount
#         FROM `tabGL Entry`
#         WHERE docstatus = 1
#           AND posting_date BETWEEN %s AND %s
#           AND party_type = 'Customer'
#     """
#     params = [year_start, year_end]
#     if default_receivable_account:
#         gl_query += " AND account = %s"
#         params.append(default_receivable_account)

#     gl_query += " GROUP BY cost_center, party, MONTH(posting_date)"
#     gl_entries = frappe.db.sql(gl_query, tuple(params), as_dict=True)

#     # Create lookup dictionary for fast access
#     gl_map = {(g.party, g.month): abs(g.amount or 0) for g in gl_entries}

#     # -----------------------------
#     # Build Report Rows
#     # -----------------------------
#     for d in records:
#         row = [d.cost_center,d.customer, d.customer_type]

#         # Monthly Details (All)
#         if filters.get("details") and filters.get("month") == "All":
#             for month in range(1, 13):
#                 achieved = gl_map.get((d.customer, month), 0)
#                 month_name = calendar.month_name[month].lower()
#                 target = flt(d.get(month_name))
#                 balance = target - achieved
#                 percent = (achieved / target * 100) if target else 0
#                 row += [target, achieved, balance, percent]

#         # Single Month
#         elif filters.get("details") and filters.get("month") != "All":
#             month_name = filters.get("month")
#             month_number = list(calendar.month_name).index(month_name)
#             achieved = gl_map.get((d.customer, month_number), 0)
#             target = flt(d.get(month_name.lower()))
#             balance = target - achieved
#             percent = (achieved / target * 100) if target else 0
#             row += [target, achieved, balance, percent]

#         # Yearly Summary
#         else:
#             total_achieved = sum(
#                 gl_map.get(( d.customer, month), 0) for month in range(1, 13)
#             )
#             target = flt(d.target_amount)
#             balance = target - total_achieved
#             percent = (total_achieved / target * 100) if target else 0
#             row += [target, total_achieved, balance, percent]

#         data.append(row)

#     return data

# # -----------------------------
# # Chart
# # -----------------------------
# def get_chart_data(filters, data):
#     if not data:
#         return None

#     total_target = 0
#     total_achieved = 0
#     total_balance = 0

#     for d in data:
#         values = d[3:]
#         if len(values) >= 4:
#             total_target += values[0]
#             total_achieved += values[1]
#             total_balance += values[2]

#     return {
#         "data": {
#             "labels": [filters.get("fiscal_year")],
#             "datasets": [
#                 {"name": _("Target"), "chartType": "bar", "values": [total_target]},
#                 {"name": _("Achieved"), "chartType": "bar", "values": [total_achieved]},
#                 {"name": _("Balance"), "chartType": "bar", "values": [total_balance]},
#             ],
#         },
#         "type": "bar",
#     }

from frappe.utils import flt, formatdate
import frappe
from frappe import _
import calendar
from erpnext.controllers.trends import get_period_date_ranges, get_period_month_ranges
from collections import defaultdict

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart_data(filters, data)
    return columns, data, None, chart

# -----------------------------
# Columns
# -----------------------------
def get_columns(filters):
    columns = [
        {"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer", "width": 180},
        {"fieldname": "customer_type", "label": "Customer Type", "fieldtype": "Data", "width": 130},
    ]

    if filters.get("details") and filters.get("month") == "All":
        for month in get_period_month_ranges("Monthly", filters["fiscal_year"]):
            short = str(month[0])[0:3]
            for suffix in ["Target", "Achieved",  "Percent"]:
                columns.append({
                    "label": f"{short} {suffix}",
                    "fieldtype": "Float",
                    "width": 120
                })
    elif filters.get("details") and filters.get("month") != "All":
        short = filters.get("month")[0:3]
        for suffix in ["Target", "Achieved",  "Percent"]:
            columns.append({
                "label": f"{short} {suffix}",
                "fieldtype": "Float",
                "width": 120
            })
    else:
        columns += [
            {"label": "Total Target", "fieldtype": "Currency", "width": 160},
            {"label": "Total Achieved", "fieldtype": "Currency", "width": 160},
            # {"label": "Total Balance", "fieldtype": "Currency", "width": 160},
            {"label": "Total Achieved Percent %", "fieldtype": "Percent", "width": 160},
        ]
    return columns

# -----------------------------
# Data
# -----------------------------
def get_data(filters):
    data = []

    # Default receivable account
    default_receivable_account = frappe.get_value("Company", filters.get("company"), "default_receivable_account")
    fiscal_year = filters.get("fiscal_year")

    # Fiscal year dates
    fy = frappe.get_doc("Fiscal Year", fiscal_year)
    year_start = fy.year_start_date
    year_end = fy.year_end_date

    # -----------------------------
    # Fetch Target Records
    # -----------------------------
    conditions = "WHERE rt.docstatus = 1 AND rt.fiscal_year = %s"
    values = [fiscal_year]

    target_query = f"""
        SELECT 
            rta.customer,
            rta.customer_type,
            rta.*
        FROM `tabCustomer Revenue Target` rt
        INNER JOIN `tabRevenue Target Customer` rta
            ON rta.parent = rt.name
        {conditions}
    """
    records = frappe.db.sql(target_query, tuple(values), as_dict=True)
    if not records:
        return data

    # -----------------------------
    # Fetch GL Entries
    # -----------------------------
    gl_query = """
        SELECT
            party,
            account,
            MONTH(posting_date) as month,
            SUM(debit - credit) as amount
        FROM `tabGL Entry`
        WHERE docstatus = 1
          AND posting_date BETWEEN %s AND %s
          AND party_type = 'Customer'
    """
    params = [year_start, year_end]
    if default_receivable_account:
        gl_query += " AND account = %s"
        params.append(default_receivable_account)

    gl_query += " GROUP BY party, MONTH(posting_date)"
    gl_entries = frappe.db.sql(gl_query, tuple(params), as_dict=True)

    # -----------------------------
    # Sum all GL entries per customer per month
    # -----------------------------
    gl_map = defaultdict(float)
    for g in gl_entries:
        gl_map[(g.party, g.month)] += flt(g.amount or 0)

    # -----------------------------
    # Build Report Rows
    # -----------------------------
    for d in records:
        row = [d.customer, d.customer_type]

        # Monthly Details (All)
        if filters.get("details") and filters.get("month") == "All":
            for month in range(1, 13):
                achieved = gl_map.get((d.customer, month), 0)
                month_name = calendar.month_name[month].lower()
                target = flt(d.get(month_name))
                # balance = target - achieved
                percent = (achieved / target * 100) if target else 0
                row += [target, achieved, percent]
                # row += [target, achieved, balance, percent]

        # Single Month
        elif filters.get("details") and filters.get("month") != "All":
            month_name = filters.get("month")
            month_number = list(calendar.month_name).index(month_name)
            achieved = gl_map.get((d.customer, month_number), 0)
            target = flt(d.get(month_name.lower()))
            # balance = target - achieved
            percent = (achieved / target * 100) if target else 0
            # row += [target, achieved, balance, percent]
            row += [target, achieved, percent]

        # Yearly Summary
        else:
            total_achieved = sum(
                gl_map.get((d.customer, month), 0) for month in range(1, 13)
            )
            target = flt(d.target_amount)
            # balance = target - total_achieved
            percent = (total_achieved / target * 100) if target else 0
            # row += [target, total_achieved, balance, percent]
            row += [target, total_achieved, percent]

        data.append(row)

    return data

# -----------------------------
# Chart
# -----------------------------
def get_chart_data(filters, data):
    if not data:
        return None

    total_target = 0
    total_achieved = 0
    # total_balance = 0

    for d in data:
        values = d[2:]  # start after customer & type
        if len(values) >= 4:
            total_target += values[0]
            total_achieved += values[1]
            # total_balance += values[2]

    return {
        "data": {
            "labels": [filters.get("fiscal_year")],
            "datasets": [
                {"name": _("Target"), "chartType": "bar", "values": [total_target]},
                {"name": _("Achieved"), "chartType": "bar", "values": [total_achieved]},
                # {"name": _("Balance"), "chartType": "bar", "values": [total_balance]},
            ],
        },
        "type": "bar",
    }