from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr, rounded, get_first_day, get_last_day
from erpnext.accounts.report.financial_statements import (
    filter_accounts, 
    set_gl_entries_by_account, 
    filter_out_zero_value_rows
)
from erpnext.accounts.report.financial_statements import get_cost_centers_with_children
from datetime import datetime, timedelta
from collections import OrderedDict


value_fields = ("opening_debit", "opening_credit", "debit", "credit", "mcredit", "mdebit", "closing_debit", "closing_credit")

def execute(filters=None):
    if not filters:
        filters = frappe._dict()
    
   # validate_filters(filters)
    data = get_data(filters)
    columns = get_columns()
    return columns, data

def validate_filters(filters):
    from datetime import datetime
    
    # Validate fiscal year first
    if not filters.get("fiscal_year"):
        frappe.throw(_("Fiscal Year is required"))

    # Get fiscal year dates
    fiscal_year = frappe.db.get_value("Fiscal Year", filters.fiscal_year, 
        ["year_start_date", "year_end_date"], as_dict=True)
    
    if not fiscal_year:
        frappe.throw(_("Fiscal Year {0} does not exist").format(filters.fiscal_year))
    
    filters.year_start_date = getdate(fiscal_year.year_start_date)
    filters.year_end_date = getdate(fiscal_year.year_end_date)

    # Handle None month - set default
    if not filters.get("month"):
        # Set default to current month
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        current_month = datetime.now().month - 1
        filters.month = month_names[current_month]

    # Validate month
    month_map = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", 
                 "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
    
    if filters.month not in month_map:
        frappe.throw(_("Invalid month: {0}. Must be Jan, Feb, Mar, etc.").format(filters.month))
    
    month_id = month_map[filters.month]
    
    # Get the month start and end dates
    year_start = filters.year_start_date
    year_end = filters.year_end_date
    
    # Generate all months in the fiscal year
    months_in_fy = []
    current = year_start
    while current <= year_end:
        months_in_fy.append(current.strftime("%Y-%m"))
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    
    # Find the selected month
    selected_month = None
    for month in months_in_fy:
        if month[-2:] == month_id:
            selected_month = month
            break
    
    if not selected_month:
        frappe.throw(_("Month {0} not found in fiscal year {1}").format(filters.month, filters.fiscal_year))
    
    actual_date = selected_month + "-01"
    filters.month_start = get_first_day(actual_date)
    filters.month_end = get_last_day(actual_date)
    
    filters.from_date = filters.year_start_date
    filters.to_date = filters.year_end_date

def get_data(filters):
    accounts = frappe.db.sql("""
        select name, parent_account, account_name, root_type, report_type, lft, rgt
        from `tabAccount` 
        where company=%s 
        and name not in ("Temporary Accounts - DS", 'Stock-Asset - DS', 'Accumulated Depreciation - DS', 
                         'Other Expenses - DS', 'Stock Expenses - DS', 'Stock Liabilities - DS', 
                         'Other Incomes - DS', 'Inventories - DS', 'BOB-A/C: 202921909 - DS') 
        order by name ASC""", filters.company, as_dict=True)

    if not accounts:
        return None

    accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)
    min_lft, max_rgt = frappe.db.sql("""select min(lft), max(rgt) from `tabAccount`
        where company=%s""", (filters.company,))[0]

    gl_entries_by_account = {}
    
    # Get month details
    month_map = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", 
                 "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
    
    if filters.month not in month_map:
        frappe.throw(_("Invalid month: {0}").format(filters.month))
    
    month_id = month_map[filters.month]
    
    # Get fiscal year dates
    fiscal_year = frappe.db.get_value("Fiscal Year", filters.fiscal_year, 
        ["year_start_date", "year_end_date"], as_dict=True)
    
    if not fiscal_year:
        frappe.throw(_("Fiscal Year {0} does not exist").format(filters.fiscal_year))
    
    start_date = getdate(fiscal_year.year_start_date)
    end_date = getdate(fiscal_year.year_end_date)
    year_start_date = start_date
    
    # Generate all months in the fiscal year
    months_in_fy = []
    current = start_date
    while current <= end_date:
        months_in_fy.append(current.strftime("%Y-%m"))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    
    # Find the selected month
    selected_month = None
    for month in months_in_fy:
        if month[-2:] == month_id:
            selected_month = month
            break
    
    if not selected_month:
        frappe.throw(_("Month {0} not found in fiscal year {1}").format(filters.month, filters.fiscal_year))
    
    actual_date = selected_month + "-01"
    month_start = get_first_day(actual_date)
    month_end = get_last_day(actual_date)
    
    # For v15, use the updated method signature
    set_gl_entries_by_account(
        filters.cost_center, 
        filters.company, 
        year_start_date, 
        month_end, 
        min_lft, 
        max_rgt, 
        gl_entries_by_account,  
        ignore_closing_entries=not flt(filters.get("with_period_closing_entry", 1))
    )

    opening_balances = get_opening_balances(filters, month_start, year_start_date)

    total_row = calculate_values(accounts, gl_entries_by_account, opening_balances, filters, month_start, month_end)
    accumulate_values_into_parents(accounts, accounts_by_name)

    data = prepare_data(accounts, filters, total_row, parent_children_map)
    data = filter_out_zero_value_rows(data, parent_children_map,
        show_zero_values=filters.get("show_zero_values"))

    return data

def get_opening_balances(filters, month_start, year_start_date):
    balance_sheet_opening = get_rootwise_opening_balances(filters, "Balance Sheet", month_start, year_start_date)
    pl_opening = get_rootwise_opening_balances(filters, "Profit and Loss", month_start, year_start_date)

    balance_sheet_opening.update(pl_opening)
    return balance_sheet_opening


def get_rootwise_opening_balances(filters, report_type, month_start, year_start_date):
    if int(str(month_start).split('-')[1]) > 7:
        start_date = str(month_start).split('-')[0] + "-06-01"
    else:
        start_date = str(int(str(month_start).split('-')[0]) - 1) + "-06-01"
    
    additional_conditions = " and posting_date >= '{0}'".format(start_date) \
        if report_type == "Profit and Loss" else " "

    if not flt(filters.get("with_period_closing_entry", 1)):
        additional_conditions += " and ifnull(voucher_type, '')!='Period Closing Voucher'"
    
    if filters.get("business_activity"):
        additional_conditions += " and business_activity = '{0}'".format(filters.business_activity)
    
    if filters.get("cost_center"):
        cost_centers = get_cost_centers_with_children(filters.cost_center)
        additional_conditions += " and cost_center IN %(cost_center)s"
    else:
        cost_centers = filters.cost_center 

    gle = frappe.db.sql("""
        select
            account, sum(debit) as opening_debit, sum(credit) as opening_credit
        from `tabGL Entry`
        where
            company=%(company)s
            {additional_conditions}
            and (posting_date < %(month_start)s or ifnull(is_opening, 'No') = 'Yes')
            and account in (select name from `tabAccount` where report_type=%(report_type)s)
            and case when voucher_type = 'Journal Entry' 
                then voucher_no not in (
                    select name from `tabJournal Entry` j 
                    where voucher_no = j.name 
                    and EXISTS(
                        select 1 from `tabJournal Entry Account` je 
                        where je.parent = j.name and je.reference_type = 'Asset'
                    ) and j.docstatus = 1
                ) 
                else 1 = 1 end
            group by account
    """.format(additional_conditions=additional_conditions),
    {
        "company": filters.company,
        "month_start": month_start,
        "report_type": report_type,
        "year_start_date": year_start_date,
        "cost_center": cost_centers
    },
    as_dict=True, debug=0)
    
    opening = frappe._dict()
    for d in gle:
        opening.setdefault(d.account, d)
    return opening

def calculate_values(accounts, gl_entries_by_account, opening_balances, filters, month_start, month_end):
    init = {
        "opening_debit": 0.0,
        "opening_credit": 0.0,
        "mdebit": 0.0,
        "debit": 0.0,
        "mcredit": 0.0,
        "credit": 0.0,
        "closing_debit": 0.0,
        "closing_credit": 0.0
    }

    total_row = {
        "account": None,
        "account_name": _("Total"),
        "warn_if_negative": True,
        "opening_debit": 0.0,
        "opening_credit": 0.0,
        "mdebit": 0.0,
        "debit": 0.0,
        "mcredit": 0.0,
        "credit": 0.0,
        "closing_debit": 0.0,
        "closing_credit": 0.0
    }
    bank_closing_credit = bank_closing_debit = cash_closing_credit = cash_closing_debit = 0
    a = b = 0

    for d in accounts:
        d.update(init.copy())

        # add opening
        d["opening_debit"] = opening_balances.get(d.name, {}).get("opening_debit", 0)
        d["opening_credit"] = opening_balances.get(d.name, {}).get("opening_credit", 0)
        
        opening = 0
        if d["account_name"] in ("a - Cash", "b - Bank", "De-Suung fund AC 202944097", "Cash in Hand"):
            opening += d["opening_debit"] - d["opening_credit"]
            if opening > 0:
                d["opening_debit"] = opening
                d["opening_credit"] = 0
            else:
                d["opening_credit"] = abs(opening)
                d["opening_debit"] = 0

        for entry in gl_entries_by_account.get(d.name, []):
            if entry.account in ("Bank & Cash - DS", "b - Bank - DS", "De-Suung fund AC 202944097 - DS"):
                d["debit"] = 0
                d["credit"] = 0
                d["mdebit"] = 0
                d["mcredit"] = 0

            if cstr(entry.is_opening) != "Yes":
                d["debit"] += flt(entry.debit, 3)
                d["credit"] += flt(entry.credit, 3)

            if entry.posting_date >= month_start and entry.posting_date <= month_end:
                d["mdebit"] += flt(entry.debit, 3)
                d["mcredit"] += flt(entry.credit, 3)

            if entry.account in ("De-Suung fund AC 202944097 - DS"):
                bank_closing_credit += d["mcredit"]
                bank_closing_debit += d["mdebit"]

            if entry.account in ("Cash in Hand - DS"):
                cash_closing_credit = d["mcredit"]
                cash_closing_debit = d["mdebit"]
            
        if d.name in ("De-Suung fund AC 202944097 - DS"):
            if a != 1:
                total_row["mcredit"] += d["opening_debit"] + d["opening_credit"]
                total_row["credit"] += d["opening_debit"] + d["opening_credit"] - d["credit"]
                a = 1

        if d.name in ("Cash in Hand - DS"):
            if b != 1:
                total_row["mcredit"] += d["opening_debit"] + d["opening_credit"]
                total_row["credit"] += d["credit"]
                b = 1

        total_row["debit"] += d["debit"]
        total_row["mdebit"] += d["mdebit"]

        if d.name not in ('De-Suung fund AC 202944097 - DS', 'Cash in Hand - DS', 'Bank & Cash - DS'):
            total_row["credit"] += d["credit"]
            total_row["mcredit"] += d["mcredit"]
    
    cb_closing_debit = cb_closing_credit = 0
    for d in accounts:
        if d["account_name"] in ('De-Suung fund AC 202944097'):
            b_amount = bank_closing_debit - bank_closing_credit + d["opening_debit"]
            if b_amount > 0:
                d["closing_debit"] = b_amount
                cb_closing_debit += b_amount
            else:
                d["closing_credit"] = abs(b_amount)
                cb_closing_credit += abs(b_amount)

        elif d["account_name"] in ("Cash in Hand"):
            c_amount = cash_closing_debit - cash_closing_credit + d["opening_debit"]
            if c_amount > 0:
                d["closing_debit"] = c_amount
                cb_closing_debit += c_amount
            else:
                d["closing_credit"] = abs(c_amount)
                cb_closing_credit += abs(c_amount)
    
    for d in accounts:
        if d["account_name"] in ("Bank & Cash - DS"):
            d["closing_debit"] = cb_closing_debit
            d["closing_credit"] = cb_closing_credit

    return total_row

def accumulate_values_into_parents(accounts, accounts_by_name):
    for d in reversed(accounts):
        if d.parent_account:
            for key in value_fields:
                accounts_by_name[d.parent_account][key] += d[key]

def prepare_data(accounts, filters, total_row, parent_children_map):
    data = []
    for d in accounts:
        has_value = False
        row = {
            "account_name": d.account_name,
            "account": d.name,
            "parent_account": d.parent_account,
            "indent": d.indent,
            "from_date": filters.from_date,
            "to_date": filters.to_date
        }
        
        # Special handling for specific accounts
        if d.name == 'Liabilities - DS':
            row["account_name"] = "Taxes"
        elif d.name == 'Bank & Cash - DS':
            row["account_name"] = "Bank & Cash"
            row["parent_account"] = ""
            row["indent"] = 0
        elif d.name == 'Releases - DS':
            row["parent_account"] = ""
            row["indent"] = 0
        
        if d.name not in ('Assets - DS'):
            prepare_opening_and_closing(d, total_row)
    
            for key in value_fields:
                row[key] = flt(d.get(key, 0.0), 3)
                if abs(row[key]) >= 0.005:
                    has_value = True
    
            row["has_value"] = has_value
            data.append(row)
    
    total_row["credit"] = total_row["credit"] - (total_row["credit"] - total_row["debit"])
    data.extend([{}, total_row])

    return data

def get_columns():
    return [
        {
            "fieldname": "account",
            "label": _("Group/Broad Head Of Account"),
            "fieldtype": "Link",
            "options": "Account",
            "width": 300
        },
        {
            "fieldname": "opening_debit",
            "label": _("Opening (Dr)"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "opening_credit",
            "label": _("Opening (Cr)"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "mcredit",
            "label": _("For the Month Credit"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "credit",
            "label": _("Annual Progressive Credit"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "mdebit",
            "label": _("For The Month Debit"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "debit",
            "label": _("Annual Progressive Debit"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "closing_debit",
            "label": _("Closing (Dr)"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "closing_credit",
            "label": _("Closing (Cr)"),
            "fieldtype": "Currency",
            "width": 120
        }
    ]

def prepare_opening_and_closing(d, total_row):
    if d["account_name"] in ('Bank & Cash'):
        if d["closing_debit"]:
            d["closing_debit"] = d["closing_debit"] / 2
        if d["closing_credit"]:
            d["closing_credit"] = d["closing_credit"] / 2

    if d["account_name"] not in ("De-Suung fund AC 202944097", "a - Cash", "Cash in Hand", "b - Bank", "Bank & Cash"):
        if d["opening_debit"] > d["opening_credit"]:
            d["opening_debit"] -= d["opening_credit"]
            d["opening_credit"] = 0.0
        else:
            d["opening_credit"] -= d["opening_debit"]
            d["opening_debit"] = 0.0

        d["closing_debit"] = d["opening_debit"] - d["mcredit"] + d["mdebit"]
        d["closing_credit"] = d["opening_credit"] - d["mdebit"] + d["mcredit"]
        
        if d["closing_debit"] > d["closing_credit"]:
            d["closing_credit"] = 0.0
        else:
            d["closing_debit"] = 0.0
    
    if d.name in ("De-Suung fund AC 202944097 - DS", "Cash in Hand - DS"):
        total_row["mdebit"] += d["closing_debit"] + d["closing_credit"]
        total_row["debit"] += d["closing_debit"] + d["closing_credit"] - d["debit"]

    if d["name"] in ("Bank & Cash - DS", "De-Suung fund AC 202944097 - DS", "b - Bank - DS"):
        d["debit"] = 0
        d["credit"] = 0
        d["mdebit"] = 0
        d["mcredit"] = 0
        
    if d["name"] in ("a - Cash - DS", "Cash in Hand - DS"):
        d["debit"] = 0
        d["mdebit"] = 0

    if d.account_name in ["Assets", "Liabilities", "Equity", "Revenue", "Expenses"]:
        total_row['opening_credit'] = total_row['opening_credit'] + d['opening_credit']
        total_row['opening_debit'] = total_row['opening_debit'] + d['opening_debit']
        total_row['closing_credit'] = total_row['closing_credit'] + d['closing_credit']
        total_row['closing_debit'] = total_row['closing_debit'] + d['closing_debit']