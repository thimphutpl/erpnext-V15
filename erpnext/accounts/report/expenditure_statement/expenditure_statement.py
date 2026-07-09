# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate

def execute(filters=None):
    if not filters:
        filters = {}
    
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "sp",
            "label": _("SP"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "ac",
            "label": _("AC"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "fic",
            "label": _("FIC"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "obc",
            "label": _("OBC"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "names",
            "label": _("Names"),
            "fieldtype": "Data",
            "width": 250
        },
        {
            "fieldname": "monthly_amount",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "monthly_personal_advance",
            "label": _("Personal Advance"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "monthly_suspense",
            "label": _("Suspense"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "annual_amount",
            "label": _("Annual Progressive Amount"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "annual_personal_advance",
            "label": _("Annual Progressive Personal Advance"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "annual_suspense",
            "label": _("Annual Progressive Suspense"),
            "fieldtype": "Currency",
            "width": 150
        }
    ]

def get_data(filters):
    # Get monthly data
    monthly_data = get_monthly_data(filters)
    
    # Get annual progressive data
    annual_data = get_annual_data(filters)
    
    # Combine monthly and annual data
    final_data = combine_data(monthly_data, annual_data)
    
    # Add summary rows
    final_data = add_summary_rows(final_data, monthly_data, annual_data, filters)
    
    return final_data

def get_monthly_data(filters):
    conditions = []
    values = {}
    
    if filters.get("company"):
        conditions.append("gle.company = %(company)s")
        values["company"] = filters.get("company")
    
    if filters.get("fiscal_year"):
        conditions.append("gle.fiscal_year = %(fiscal_year)s")
        values["fiscal_year"] = filters.get("fiscal_year")
    
    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("gle.posting_date BETWEEN %(from_date)s AND %(to_date)s")
        values["from_date"] = filters.get("from_date")
        values["to_date"] = filters.get("to_date")
    
    if filters.get("cost_center"):
        conditions.append("gle.cost_center = %(cost_center)s")
        values["cost_center"] = filters.get("cost_center")
    
    # Only include GL entries with budget_activity
    conditions.append("gle.budget_activity IS NOT NULL")
    conditions.append("gle.budget_activity != ''")
    conditions.append("gle.is_cancelled = 0")
    
    where_clause = " AND ".join(conditions)
    
    sql_query = """
        SELECT 
            cc.cost_center_number AS sp,
            ba.activity_code AS ac,
            sof.fic AS fic,
            acc.account_number AS obc,
            acc.name AS account_name,
            acc.parent_account,
            -- Monthly amounts by type
            SUM(IF(acc.parent_account LIKE '%%10 a - Current - RBA%%' OR acc.parent_account = '10 a - Current - RBA', 
                (gle.debit - gle.credit), 0)) AS monthly_current,
            SUM(IF(acc.parent_account LIKE '%%10 b - Capital - RBA%%' OR acc.parent_account = '10 b - Capital - RBA', 
                (gle.debit - gle.credit), 0)) AS monthly_capital,
            SUM(IF(acc.parent_account LIKE '%%10 c - Lending - RBA%%' OR acc.parent_account = '10 c - Lending - RBA', 
                (gle.debit - gle.credit), 0)) AS monthly_lending,
            SUM(IF(acc.parent_account LIKE '%%10 d - Repayment - RBG%%' OR acc.parent_account = '10 d - Repayment - RBG', 
                (gle.debit - gle.credit), 0)) AS monthly_repayment,
            -- Personal Advance (88.01)
            SUM(IF(acc.account_number = '88.01', (gle.debit - gle.credit), 0)) AS monthly_personal_advance,
            -- Suspense
            SUM(IF(acc.account_number IN ('88.02', '89.01', '89.02'), (gle.debit - gle.credit), 0)) AS monthly_suspense
        FROM 
            `tabGL Entry` gle
        LEFT JOIN 
            `tabCost Center` cc ON gle.cost_center = cc.name
        LEFT JOIN 
            `tabBudget Activity` ba ON gle.budget_activity = ba.name
        LEFT JOIN 
            `tabSource of Fund` sof ON gle.source_of_fund = sof.name
        LEFT JOIN 
            `tabAccount` acc ON gle.account = acc.name
        WHERE 
            {where_clause}
        GROUP BY 
            cc.cost_center_number,
            ba.activity_code,
            sof.fic,
            acc.account_number,
            acc.name,
            acc.parent_account
    """.format(where_clause=where_clause)
    
    return frappe.db.sql(sql_query, values, as_dict=1)

def get_annual_data(filters):
    # Get annual progressive data from start of fiscal year to selected to_date
    fiscal_year = filters.get("fiscal_year")
    if not fiscal_year:
        return []
    
    fy_data = frappe.db.get_value("Fiscal Year", fiscal_year, 
        ["year_start_date", "year_end_date"], as_dict=True)
    
    if not fy_data:
        return []
    
    annual_filters = {
        "company": filters.get("company"),
        "fiscal_year": filters.get("fiscal_year"),
        "from_date": fy_data.year_start_date,
        "to_date": filters.get("to_date", fy_data.year_end_date)
    }
    
    if filters.get("cost_center"):
        annual_filters["cost_center"] = filters.get("cost_center")
    
    conditions = []
    values = {}
    
    if annual_filters.get("company"):
        conditions.append("gle.company = %(company)s")
        values["company"] = annual_filters.get("company")
    
    if annual_filters.get("fiscal_year"):
        conditions.append("gle.fiscal_year = %(fiscal_year)s")
        values["fiscal_year"] = annual_filters.get("fiscal_year")
    
    if annual_filters.get("from_date") and annual_filters.get("to_date"):
        conditions.append("gle.posting_date BETWEEN %(from_date)s AND %(to_date)s")
        values["from_date"] = annual_filters.get("from_date")
        values["to_date"] = annual_filters.get("to_date")
    
    if annual_filters.get("cost_center"):
        conditions.append("gle.cost_center = %(cost_center)s")
        values["cost_center"] = annual_filters.get("cost_center")
    
    conditions.append("gle.budget_activity IS NOT NULL")
    conditions.append("gle.budget_activity != ''")
    conditions.append("gle.is_cancelled = 0")
    
    where_clause = " AND ".join(conditions)
    
    sql_query = """
        SELECT 
            cc.cost_center_number AS sp,
            ba.activity_code AS ac,
            sof.fic AS fic,
            acc.account_number AS obc,
            -- Annual amounts by type
            SUM(IF(acc.parent_account LIKE '%%10 a - Current - RBA%%' OR acc.parent_account = '10 a - Current - RBA', 
                (gle.debit - gle.credit), 0)) AS annual_current,
            SUM(IF(acc.parent_account LIKE '%%10 b - Capital - RBA%%' OR acc.parent_account = '10 b - Capital - RBA', 
                (gle.debit - gle.credit), 0)) AS annual_capital,
            SUM(IF(acc.parent_account LIKE '%%10 c - Lending - RBA%%' OR acc.parent_account = '10 c - Lending - RBA', 
                (gle.debit - gle.credit), 0)) AS annual_lending,
            SUM(IF(acc.parent_account LIKE '%%10 d - Repayment - RBG%%' OR acc.parent_account = '10 d - Repayment - RBG', 
                (gle.debit - gle.credit), 0)) AS annual_repayment,
            -- Annual Personal Advance (88.01)
            SUM(IF(acc.account_number = '88.01', (gle.debit - gle.credit), 0)) AS annual_personal_advance,
            -- Annual Suspense
            SUM(IF(acc.account_number IN ('88.02', '89.01', '89.02'), (gle.debit - gle.credit), 0)) AS annual_suspense
        FROM 
            `tabGL Entry` gle
        LEFT JOIN 
            `tabCost Center` cc ON gle.cost_center = cc.name
        LEFT JOIN 
            `tabBudget Activity` ba ON gle.budget_activity = ba.name
        LEFT JOIN 
            `tabSource of Fund` sof ON gle.source_of_fund = sof.name
        LEFT JOIN 
            `tabAccount` acc ON gle.account = acc.name
        WHERE 
            {where_clause}
        GROUP BY 
            cc.cost_center_number,
            ba.activity_code,
            sof.fic,
            acc.account_number
    """.format(where_clause=where_clause)
    
    return frappe.db.sql(sql_query, values, as_dict=1)

def combine_data(monthly_data, annual_data):
    final_data = []
    
    # Create a dictionary for quick lookup of annual data
    annual_dict = {}
    for row in annual_data:
        key = (row.get("sp"), row.get("ac"), row.get("fic"), row.get("obc"))
        annual_dict[key] = row
    
    # Combine monthly and annual data
    for monthly_row in monthly_data:
        key = (monthly_row.get("sp"), monthly_row.get("ac"), 
               monthly_row.get("fic"), monthly_row.get("obc"))
        
        annual_row = annual_dict.get(key, {})
        
        # Calculate total amounts
        monthly_amount = (flt(monthly_row.get("monthly_current", 0)) + 
                         flt(monthly_row.get("monthly_capital", 0)) + 
                         flt(monthly_row.get("monthly_lending", 0)) + 
                         flt(monthly_row.get("monthly_repayment", 0)))
        
        annual_amount = (flt(annual_row.get("annual_current", 0)) + 
                        flt(annual_row.get("annual_capital", 0)) + 
                        flt(annual_row.get("annual_lending", 0)) + 
                        flt(annual_row.get("annual_repayment", 0)))
        
        final_row = {
            "sp": monthly_row.get("sp", ""),
            "ac": monthly_row.get("ac", ""),
            "fic": monthly_row.get("fic", ""),
            "obc": monthly_row.get("obc", ""),
            "names": monthly_row.get("account_name", ""),
            "monthly_current": flt(monthly_row.get("monthly_current", 0)),
            "monthly_capital": flt(monthly_row.get("monthly_capital", 0)),
            "monthly_lending": flt(monthly_row.get("monthly_lending", 0)),
            "monthly_repayment": flt(monthly_row.get("monthly_repayment", 0)),
            "monthly_amount": monthly_amount,
            "monthly_personal_advance": flt(monthly_row.get("monthly_personal_advance", 0)),
            "monthly_suspense": flt(monthly_row.get("monthly_suspense", 0)),
            "annual_current": flt(annual_row.get("annual_current", 0)),
            "annual_capital": flt(annual_row.get("annual_capital", 0)),
            "annual_lending": flt(annual_row.get("annual_lending", 0)),
            "annual_repayment": flt(annual_row.get("annual_repayment", 0)),
            "annual_amount": annual_amount,
            "annual_personal_advance": flt(annual_row.get("annual_personal_advance", 0)),
            "annual_suspense": flt(annual_row.get("annual_suspense", 0))
        }
        
        # Only include rows with amounts
        if (final_row["monthly_amount"] != 0 or 
            final_row["annual_amount"] != 0 or
            final_row["monthly_personal_advance"] != 0 or
            final_row["annual_personal_advance"] != 0):
            final_data.append(final_row)
    
    # Sort the data
    final_data.sort(key=lambda x: (x["sp"], x["ac"], x["fic"], x["obc"]))
    
    return final_data

def add_summary_rows(final_data, monthly_data, annual_data, filters):
    if not final_data:
        return final_data
    
    # Calculate totals from the raw data
    monthly_totals = {
        "current": 0,
        "capital": 0,
        "lending": 0,
        "repayment": 0,
        "personal_advance": 0,
        "suspense": 0
    }
    
    annual_totals = {
        "current": 0,
        "capital": 0,
        "lending": 0,
        "repayment": 0,
        "personal_advance": 0,
        "suspense": 0
    }
    
    # Sum monthly totals
    for row in monthly_data:
        monthly_totals["current"] += flt(row.get("monthly_current", 0))
        monthly_totals["capital"] += flt(row.get("monthly_capital", 0))
        monthly_totals["lending"] += flt(row.get("monthly_lending", 0))
        monthly_totals["repayment"] += flt(row.get("monthly_repayment", 0))
        monthly_totals["personal_advance"] += flt(row.get("monthly_personal_advance", 0))
        monthly_totals["suspense"] += flt(row.get("monthly_suspense", 0))
    
    # Sum annual totals
    for row in annual_data:
        annual_totals["current"] += flt(row.get("annual_current", 0))
        annual_totals["capital"] += flt(row.get("annual_capital", 0))
        annual_totals["lending"] += flt(row.get("annual_lending", 0))
        annual_totals["repayment"] += flt(row.get("annual_repayment", 0))
        annual_totals["personal_advance"] += flt(row.get("annual_personal_advance", 0))
        annual_totals["suspense"] += flt(row.get("annual_suspense", 0))
    
    # Helper function to add breakdown rows for a section
    def add_breakdown_rows(section_name):
        rows = []
        
        # Section header
        rows.append({
            "sp": "",
            "ac": "",
            "fic": "",
            "obc": "",
            "names": section_name,
            "monthly_current": 0,
            "monthly_capital": 0,
            "monthly_lending": 0,
            "monthly_repayment": 0,
            "monthly_amount": 0,
            "monthly_personal_advance": 0,
            "monthly_suspense": 0,
            "annual_current": 0,
            "annual_capital": 0,
            "annual_lending": 0,
            "annual_repayment": 0,
            "annual_amount": 0,
            "annual_personal_advance": 0,
            "annual_suspense": 0,
            "is_summary": 1,
            "indent": 0,
            "is_section_header": 1
        })
        
        # Add Current (Total)
        rows.append({
            "sp": "",
            "ac": "",
            "fic": "",
            "obc": "",
            "names": "Current (Total)",
            "monthly_current": monthly_totals["current"],
            "monthly_capital": 0,
            "monthly_lending": 0,
            "monthly_repayment": 0,
            "monthly_amount": monthly_totals["current"],
            "monthly_personal_advance": monthly_totals["personal_advance"],
            "monthly_suspense": monthly_totals["suspense"],
            "annual_current": annual_totals["current"],
            "annual_capital": 0,
            "annual_lending": 0,
            "annual_repayment": 0,
            "annual_amount": annual_totals["current"],
            "annual_personal_advance": annual_totals["personal_advance"],
            "annual_suspense": annual_totals["suspense"],
            "is_summary": 1,
            "indent": 1,
            "is_breakdown": 1
        })
        
        # Add Capital (Total)
        rows.append({
            "sp": "",
            "ac": "",
            "fic": "",
            "obc": "",
            "names": "Capital (Total)",
            "monthly_current": 0,
            "monthly_capital": monthly_totals["capital"],
            "monthly_lending": 0,
            "monthly_repayment": 0,
            "monthly_amount": monthly_totals["capital"],
            "monthly_personal_advance": 0,
            "monthly_suspense": 0,
            "annual_current": 0,
            "annual_capital": annual_totals["capital"],
            "annual_lending": 0,
            "annual_repayment": 0,
            "annual_amount": annual_totals["capital"],
            "annual_personal_advance": 0,
            "annual_suspense": 0,
            "is_summary": 1,
            "indent": 1,
            "is_breakdown": 1
        })
        
        # Add Lending (Total)
        rows.append({
            "sp": "",
            "ac": "",
            "fic": "",
            "obc": "",
            "names": "Lending (Total)",
            "monthly_current": 0,
            "monthly_capital": 0,
            "monthly_lending": monthly_totals["lending"],
            "monthly_repayment": 0,
            "monthly_amount": monthly_totals["lending"],
            "monthly_personal_advance": 0,
            "monthly_suspense": 0,
            "annual_current": 0,
            "annual_capital": 0,
            "annual_lending": annual_totals["lending"],
            "annual_repayment": 0,
            "annual_amount": annual_totals["lending"],
            "annual_personal_advance": 0,
            "annual_suspense": 0,
            "is_summary": 1,
            "indent": 1,
            "is_breakdown": 1
        })
        
        # Add Repayment (Total)
        rows.append({
            "sp": "",
            "ac": "",
            "fic": "",
            "obc": "",
            "names": "Repayment (Total)",
            "monthly_current": 0,
            "monthly_capital": 0,
            "monthly_lending": 0,
            "monthly_repayment": monthly_totals["repayment"],
            "monthly_amount": monthly_totals["repayment"],
            "monthly_personal_advance": 0,
            "monthly_suspense": 0,
            "annual_current": 0,
            "annual_capital": 0,
            "annual_lending": 0,
            "annual_repayment": annual_totals["repayment"],
            "annual_amount": annual_totals["repayment"],
            "annual_personal_advance": 0,
            "annual_suspense": 0,
            "is_summary": 1,
            "indent": 1,
            "is_breakdown": 1
        })
        
        return rows
    
    # Add blank row before Total OBC/GL
    final_data.append({
        "sp": "",
        "ac": "",
        "fic": "",
        "obc": "",
        "names": "",
        "monthly_amount": 0,
        "annual_amount": 0,
        "is_summary": 1,
        "indent": 0
    })
    
    # Add Total OBC/GL section with breakdown rows
    final_data.extend(add_breakdown_rows("Total OBC/GL"))
    
    # Add blank row for spacing
    final_data.append({
        "sp": "",
        "ac": "",
        "fic": "",
        "obc": "",
        "names": "",
        "monthly_amount": 0,
        "annual_amount": 0,
        "is_summary": 1,
        "indent": 0
    })
    
    # Add Total Activity section with breakdown rows
    final_data.extend(add_breakdown_rows("Total Activity"))
    
    # Add blank row for spacing
    final_data.append({
        "sp": "",
        "ac": "",
        "fic": "",
        "obc": "",
        "names": "",
        "monthly_amount": 0,
        "annual_amount": 0,
        "is_summary": 1,
        "indent": 0
    })
    
    # Add Total Sub-program section with breakdown rows
    final_data.extend(add_breakdown_rows("Total Sub-program"))
    
    # Add blank row for spacing
    final_data.append({
        "sp": "",
        "ac": "",
        "fic": "",
        "obc": "",
        "names": "",
        "monthly_amount": 0,
        "annual_amount": 0,
        "is_summary": 1,
        "indent": 0
    })
    
    # Add Total Program section with breakdown rows
    final_data.extend(add_breakdown_rows("Total Program"))
    
    return final_data