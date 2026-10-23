# from __future__ import unicode_literals
# import frappe
# from frappe import _
# from frappe.utils import flt, getdate, formatdate, cstr, rounded, get_first_day, get_last_day
# from erpnext.accounts.report.financial_statements import (
#     filter_accounts, 
#     set_gl_entries_by_account, 
#     filter_out_zero_value_rows
# )
# from erpnext.accounts.report.financial_statements import get_cost_centers_with_children
# from datetime import datetime, timedelta
# from collections import OrderedDict


# value_fields = ("opening_debit", "opening_credit", "debit", "credit", "mcredit", "mdebit", "closing_debit", "closing_credit")

# def execute(filters=None):
#     if not filters:
#         filters = frappe._dict()
    
#    # validate_filters(filters)
#     data = get_data(filters)
#     columns = get_columns()
#     return columns, data

# def validate_filters(filters):
#     from datetime import datetime
    
#     # Validate fiscal year first
#     if not filters.get("fiscal_year"):
#         frappe.throw(_("Fiscal Year is required"))

#     # Get fiscal year dates
#     fiscal_year = frappe.db.get_value("Fiscal Year", filters.fiscal_year, 
#         ["year_start_date", "year_end_date"], as_dict=True)
    
#     if not fiscal_year:
#         frappe.throw(_("Fiscal Year {0} does not exist").format(filters.fiscal_year))
    
#     filters.year_start_date = getdate(fiscal_year.year_start_date)
#     filters.year_end_date = getdate(fiscal_year.year_end_date)

#     # Handle None month - set default
#     if not filters.get("month"):
#         # Set default to current month
#         month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
#         current_month = datetime.now().month - 1
#         filters.month = month_names[current_month]

#     # Validate month
#     month_map = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", 
#                  "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
    
#     if filters.month not in month_map:
#         frappe.throw(_("Invalid month: {0}. Must be Jan, Feb, Mar, etc.").format(filters.month))
    
#     month_id = month_map[filters.month]
    
#     # Get the month start and end dates
#     year_start = filters.year_start_date
#     year_end = filters.year_end_date
    
#     # Generate all months in the fiscal year
#     months_in_fy = []
#     current = year_start
#     while current <= year_end:
#         months_in_fy.append(current.strftime("%Y-%m"))
#         # Move to next month
#         if current.month == 12:
#             current = current.replace(year=current.year + 1, month=1)
#         else:
#             current = current.replace(month=current.month + 1)
    
#     # Find the selected month
#     selected_month = None
#     for month in months_in_fy:
#         if month[-2:] == month_id:
#             selected_month = month
#             break
    
#     if not selected_month:
#         frappe.throw(_("Month {0} not found in fiscal year {1}").format(filters.month, filters.fiscal_year))
    
#     actual_date = selected_month + "-01"
#     filters.month_start = get_first_day(actual_date)
#     filters.month_end = get_last_day(actual_date)
    
#     filters.from_date = filters.year_start_date
#     filters.to_date = filters.year_end_date

# def get_data(filters):
#     accounts = frappe.db.sql("""
#         select name, parent_account, account_name, root_type, report_type, lft, rgt
#         from `tabAccount` 
#         where company=%s 
#         and name not in ("Temporary Accounts - DS", 'Stock-Asset - DS', 'Accumulated Depreciation - DS', 
#                          'Other Expenses - DS', 'Stock Expenses - DS', 'Stock Liabilities - DS', 
#                          'Other Incomes - DS', 'Inventories - DS', 'BOB-A/C: 202921909 - DS') 
#         order by name ASC""", filters.company, as_dict=True)

#     if not accounts:
#         return None

#     accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)
#     min_lft, max_rgt = frappe.db.sql("""select min(lft), max(rgt) from `tabAccount`
#         where company=%s""", (filters.company,))[0]

#     gl_entries_by_account = {}
    
#     # Get month details
#     month_map = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", 
#                  "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
    
#     if filters.month not in month_map:
#         frappe.throw(_("Invalid month: {0}").format(filters.month))
    
#     month_id = month_map[filters.month]
    
#     # Get fiscal year dates
#     fiscal_year = frappe.db.get_value("Fiscal Year", filters.fiscal_year, 
#         ["year_start_date", "year_end_date"], as_dict=True)
    
#     if not fiscal_year:
#         frappe.throw(_("Fiscal Year {0} does not exist").format(filters.fiscal_year))
    
#     start_date = getdate(fiscal_year.year_start_date)
#     end_date = getdate(fiscal_year.year_end_date)
#     year_start_date = start_date
    
#     # Generate all months in the fiscal year
#     months_in_fy = []
#     current = start_date
#     while current <= end_date:
#         months_in_fy.append(current.strftime("%Y-%m"))
#         if current.month == 12:
#             current = current.replace(year=current.year + 1, month=1)
#         else:
#             current = current.replace(month=current.month + 1)
    
#     # Find the selected month
#     selected_month = None
#     for month in months_in_fy:
#         if month[-2:] == month_id:
#             selected_month = month
#             break
    
#     if not selected_month:
#         frappe.throw(_("Month {0} not found in fiscal year {1}").format(filters.month, filters.fiscal_year))
    
#     actual_date = selected_month + "-01"
#     month_start = get_first_day(actual_date)
#     month_end = get_last_day(actual_date)
    
#     # For v15, use the updated method signature
#     set_gl_entries_by_account(
#         filters.cost_center, 
#         filters.company, 
#         year_start_date, 
#         month_end, 
#         min_lft, 
#         max_rgt, 
#         gl_entries_by_account,  
#         ignore_closing_entries=not flt(filters.get("with_period_closing_entry", 1))
#     )

#     opening_balances = get_opening_balances(filters, month_start, year_start_date)

#     total_row = calculate_values(accounts, gl_entries_by_account, opening_balances, filters, month_start, month_end)
#     accumulate_values_into_parents(accounts, accounts_by_name)

#     data = prepare_data(accounts, filters, total_row, parent_children_map)
#     data = filter_out_zero_value_rows(data, parent_children_map,
#         show_zero_values=filters.get("show_zero_values"))

#     return data

# def get_opening_balances(filters, month_start, year_start_date):
#     balance_sheet_opening = get_rootwise_opening_balances(filters, "Balance Sheet", month_start, year_start_date)
#     pl_opening = get_rootwise_opening_balances(filters, "Profit and Loss", month_start, year_start_date)

#     balance_sheet_opening.update(pl_opening)
#     return balance_sheet_opening


# def get_rootwise_opening_balances(filters, report_type, month_start, year_start_date):
#     if int(str(month_start).split('-')[1]) > 7:
#         start_date = str(month_start).split('-')[0] + "-06-01"
#     else:
#         start_date = str(int(str(month_start).split('-')[0]) - 1) + "-06-01"
    
#     additional_conditions = " and posting_date >= '{0}'".format(start_date) \
#         if report_type == "Profit and Loss" else " "

#     if not flt(filters.get("with_period_closing_entry", 1)):
#         additional_conditions += " and ifnull(voucher_type, '')!='Period Closing Voucher'"
    
#     if filters.get("business_activity"):
#         additional_conditions += " and business_activity = '{0}'".format(filters.business_activity)
    
#     if filters.get("cost_center"):
#         cost_centers = get_cost_centers_with_children(filters.cost_center)
#         additional_conditions += " and cost_center IN %(cost_center)s"
#     else:
#         cost_centers = filters.cost_center 

#     gle = frappe.db.sql("""
#         select
#             account, sum(debit) as opening_debit, sum(credit) as opening_credit
#         from `tabGL Entry`
#         where
#             company=%(company)s
#             {additional_conditions}
#             and (posting_date < %(month_start)s or ifnull(is_opening, 'No') = 'Yes')
#             and account in (select name from `tabAccount` where report_type=%(report_type)s)
#             and case when voucher_type = 'Journal Entry' 
#                 then voucher_no not in (
#                     select name from `tabJournal Entry` j 
#                     where voucher_no = j.name 
#                     and EXISTS(
#                         select 1 from `tabJournal Entry Account` je 
#                         where je.parent = j.name and je.reference_type = 'Asset'
#                     ) and j.docstatus = 1
#                 ) 
#                 else 1 = 1 end
#             group by account
#     """.format(additional_conditions=additional_conditions),
#     {
#         "company": filters.company,
#         "month_start": month_start,
#         "report_type": report_type,
#         "year_start_date": year_start_date,
#         "cost_center": cost_centers
#     },
#     as_dict=True, debug=0)
    
#     opening = frappe._dict()
#     for d in gle:
#         opening.setdefault(d.account, d)
#     return opening

# def calculate_values(accounts, gl_entries_by_account, opening_balances, filters, month_start, month_end):
#     init = {
#         "opening_debit": 0.0,
#         "opening_credit": 0.0,
#         "mdebit": 0.0,
#         "debit": 0.0,
#         "mcredit": 0.0,
#         "credit": 0.0,
#         "closing_debit": 0.0,
#         "closing_credit": 0.0
#     }

#     total_row = {
#         "account": None,
#         "account_name": _("Total"),
#         "warn_if_negative": True,
#         "opening_debit": 0.0,
#         "opening_credit": 0.0,
#         "mdebit": 0.0,
#         "debit": 0.0,
#         "mcredit": 0.0,
#         "credit": 0.0,
#         "closing_debit": 0.0,
#         "closing_credit": 0.0
#     }
#     bank_closing_credit = bank_closing_debit = cash_closing_credit = cash_closing_debit = 0
#     a = b = 0

#     for d in accounts:
#         d.update(init.copy())

#         # add opening
#         d["opening_debit"] = opening_balances.get(d.name, {}).get("opening_debit", 0)
#         d["opening_credit"] = opening_balances.get(d.name, {}).get("opening_credit", 0)
        
#         opening = 0
#         if d["account_name"] in ("a - Cash", "b - Bank", "De-Suung fund AC 202944097", "Cash in Hand", "De-Suung fund AC 202944097 - DS", "1.01 - Pay & Allowances - RBA", "24.03 - Contributions - Provident Fund - RBA", "80.02 - Bank Transactions - RBA"):
#             opening += d["opening_debit"] - d["opening_credit"]
#             if opening > 0:
#                 d["opening_debit"] = opening
#                 d["opening_credit"] = 0
#             else:
#                 d["opening_credit"] = abs(opening)
#                 d["opening_debit"] = 0

#         for entry in gl_entries_by_account.get(d.name, []):
#             if entry.account in ("Bank & Cash - DS", "b - Bank - DS", "De-Suung fund AC 202944097 - DS", "1.01 - Pay & Allowances - RBA", "24.03 - Contributions - Provident Fund - RBA", "80.02 - Bank Transactions - RBA"):
#                 d["debit"] = 0
#                 d["credit"] = 0
#                 d["mdebit"] = 0
#                 d["mcredit"] = 0

#             if cstr(entry.is_opening) != "Yes":
#                 d["debit"] += flt(entry.debit, 3)
#                 d["credit"] += flt(entry.credit, 3)

#             if entry.posting_date >= month_start and entry.posting_date <= month_end:
#                 d["mdebit"] += flt(entry.debit, 3)
#                 d["mcredit"] += flt(entry.credit, 3)

#             if entry.account in ("De-Suung fund AC 202944097 - DS"):
#                 bank_closing_credit += d["mcredit"]
#                 bank_closing_debit += d["mdebit"]

#             if entry.account in ("Cash in Hand - DS"):
#                 cash_closing_credit = d["mcredit"]
#                 cash_closing_debit = d["mdebit"]
            
#         if d.name in ("De-Suung fund AC 202944097 - DS"):
#             if a != 1:
#                 total_row["mcredit"] += d["opening_debit"] + d["opening_credit"]
#                 total_row["credit"] += d["opening_debit"] + d["opening_credit"] - d["credit"]
#                 a = 1

#         if d.name in ("Cash in Hand - DS"):
#             if b != 1:
#                 total_row["mcredit"] += d["opening_debit"] + d["opening_credit"]
#                 total_row["credit"] += d["credit"]
#                 b = 1

#         total_row["debit"] += d["debit"]
#         total_row["mdebit"] += d["mdebit"]

#         if d.name not in ('De-Suung fund AC 202944097 - DS', 'Cash in Hand - DS', 'Bank & Cash - DS'):
#             total_row["credit"] += d["credit"]
#             total_row["mcredit"] += d["mcredit"]
    
#     cb_closing_debit = cb_closing_credit = 0
#     for d in accounts:
#         if d["account_name"] in ('De-Suung fund AC 202944097'):
#             b_amount = bank_closing_debit - bank_closing_credit + d["opening_debit"]
#             if b_amount > 0:
#                 d["closing_debit"] = b_amount
#                 cb_closing_debit += b_amount
#             else:
#                 d["closing_credit"] = abs(b_amount)
#                 cb_closing_credit += abs(b_amount)

#         elif d["account_name"] in ("Cash in Hand"):
#             c_amount = cash_closing_debit - cash_closing_credit + d["opening_debit"]
#             if c_amount > 0:
#                 d["closing_debit"] = c_amount
#                 cb_closing_debit += c_amount
#             else:
#                 d["closing_credit"] = abs(c_amount)
#                 cb_closing_credit += abs(c_amount)
    
#     for d in accounts:
#         if d["account_name"] in ("Bank & Cash - DS"):
#             d["closing_debit"] = cb_closing_debit
#             d["closing_credit"] = cb_closing_credit

#     return total_row

# def accumulate_values_into_parents(accounts, accounts_by_name):
#     for d in reversed(accounts):
#         if d.parent_account:
#             for key in value_fields:
#                 accounts_by_name[d.parent_account][key] += d[key]

# def prepare_data(accounts, filters, total_row, parent_children_map):
#     data = []
#     for d in accounts:
#         has_value = False
#         row = {
#             "account_name": d.account_name,
#             "account": d.name,
#             "parent_account": d.parent_account,
#             "indent": d.indent,
#             "from_date": filters.from_date,
#             "to_date": filters.to_date
#         }
        
#         # Special handling for specific accounts
#         if d.name == 'Liabilities - DS':
#             row["account_name"] = "Taxes"
#         elif d.name == 'Bank & Cash - DS':
#             row["account_name"] = "Bank & Cash"
#             row["parent_account"] = ""
#             row["indent"] = 0
#         elif d.name == 'Releases - DS':
#             row["parent_account"] = ""
#             row["indent"] = 0
        
#         if d.name not in ('Assets - DS'):
#             prepare_opening_and_closing(d, total_row)
    
#             for key in value_fields:
#                 row[key] = flt(d.get(key, 0.0), 3)
#                 if abs(row[key]) >= 0.005:
#                     has_value = True
    
#             row["has_value"] = has_value
#             data.append(row)
    
#     total_row["credit"] = total_row["credit"] - (total_row["credit"] - total_row["debit"])
#     data.extend([{}, total_row])

#     return data

# def get_columns():
#     return [
#         {
#             "fieldname": "account",
#             "label": _("Group/Broad Head Of Account"),
#             "fieldtype": "Link",
#             "options": "Account",
#             "width": 300
#         },
#         {
#             "fieldname": "opening_debit",
#             "label": _("Opening (Dr)"),
#             "fieldtype": "Currency",
#             "width": 120
#         },
#         {
#             "fieldname": "opening_credit",
#             "label": _("Opening (Cr)"),
#             "fieldtype": "Currency",
#             "width": 120
#         },
#         {
#             "fieldname": "mcredit",
#             "label": _("For the Month Credit"),
#             "fieldtype": "Currency",
#             "width": 120
#         },
#         {
#             "fieldname": "credit",
#             "label": _("Annual Progressive Credit"),
#             "fieldtype": "Currency",
#             "width": 120
#         },
#         {
#             "fieldname": "mdebit",
#             "label": _("For The Month Debit"),
#             "fieldtype": "Currency",
#             "width": 120
#         },
#         {
#             "fieldname": "debit",
#             "label": _("Annual Progressive Debit"),
#             "fieldtype": "Currency",
#             "width": 120
#         },
#         {
#             "fieldname": "closing_debit",
#             "label": _("Closing (Dr)"),
#             "fieldtype": "Currency",
#             "width": 120
#         },
#         {
#             "fieldname": "closing_credit",
#             "label": _("Closing (Cr)"),
#             "fieldtype": "Currency",
#             "width": 120
#         }
#     ]

# def prepare_opening_and_closing(d, total_row):
#     if d["account_name"] in ('Bank & Cash'):
#         if d["closing_debit"]:
#             d["closing_debit"] = d["closing_debit"] / 2
#         if d["closing_credit"]:
#             d["closing_credit"] = d["closing_credit"] / 2

#     if d["account_name"] not in ("De-Suung fund AC 202944097", "a - Cash", "Cash in Hand", "b - Bank", "Bank & Cash"):
#         if d["opening_debit"] > d["opening_credit"]:
#             d["opening_debit"] -= d["opening_credit"]
#             d["opening_credit"] = 0.0
#         else:
#             d["opening_credit"] -= d["opening_debit"]
#             d["opening_debit"] = 0.0

#         d["closing_debit"] = d["opening_debit"] - d["mcredit"] + d["mdebit"]
#         d["closing_credit"] = d["opening_credit"] - d["mdebit"] + d["mcredit"]
        
#         if d["closing_debit"] > d["closing_credit"]:
#             d["closing_credit"] = 0.0
#         else:
#             d["closing_debit"] = 0.0
    
#     if d.name in ("De-Suung fund AC 202944097 - DS", "Cash in Hand - DS"):
#         total_row["mdebit"] += d["closing_debit"] + d["closing_credit"]
#         total_row["debit"] += d["closing_debit"] + d["closing_credit"] - d["debit"]

#     if d["name"] in ("Bank & Cash - DS", "De-Suung fund AC 202944097 - DS", "b - Bank - DS"):
#         d["debit"] = 0
#         d["credit"] = 0
#         d["mdebit"] = 0
#         d["mcredit"] = 0
        
#     if d["name"] in ("a - Cash - DS", "Cash in Hand - DS"):
#         d["debit"] = 0
#         d["mdebit"] = 0

#     if d.account_name in ["Assets", "Liabilities", "Equity", "Revenue", "Expenses"]:
#         total_row['opening_credit'] = total_row['opening_credit'] + d['opening_credit']
#         total_row['opening_debit'] = total_row['opening_debit'] + d['opening_debit']
#         total_row['closing_credit'] = total_row['closing_credit'] + d['closing_credit']
#         total_row['closing_debit'] = total_row['closing_debit'] + d['closing_debit']



# import frappe
# from frappe import _
# from frappe.utils import get_last_day, getdate, flt


# def execute(filters=None):
#     filters = frappe._dict(filters or {})
#     validate_filters(filters)

#     columns = get_columns()
#     data = get_data(filters)

#     return columns, data


# def validate_filters(filters):
#     for field in ("company", "fiscal_year", "month"):
#         if not filters.get(field):
#             frappe.throw(_("Please select {0}").format(field.replace("_", " ").title()))

#     if not frappe.db.exists("Company", filters.company):
#         frappe.throw(_("Invalid Company"))

#     fiscal_year = frappe.db.get_value(
#         "Fiscal Year",
#         filters.fiscal_year,
#         ["year_start_date", "year_end_date"],
#         as_dict=True,
#     )
#     if not fiscal_year:
#         frappe.throw(_("Fiscal Year not found"))

#     filters.year_start = getdate(fiscal_year.year_start_date)
#     filters.year_end = getdate(fiscal_year.year_end_date)

#     month_map = {
#         "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
#         "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
#         "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
#     }
#     month_number = month_map.get(filters.month)
#     if not month_number:
#         frappe.throw(_("Invalid Month"))

#     month_year = filters.year_start.year + (
#         1 if month_number < filters.year_start.month else 0
#     )
#     filters.month_start = getdate(
#         f"{month_year}-{month_number:02d}-01"
#     )
#     filters.month_end = get_last_day(filters.month_start)

#     if (
#         filters.month_start < filters.year_start
#         or filters.month_start > filters.year_end
#     ):
#         frappe.throw(
#             _("Selected month does not belong to the selected Fiscal Year")
#         )

#     filters.progressive_end = min(filters.month_end, filters.year_end)
#     filters.with_period_closing_entry = int(
#         filters.get("with_period_closing_entry") or 0
#     )


# def get_columns():
#     return [
#         {
#             "fieldname": "account",
#             "label": _("Group/Broad Head Of Account"),
#             "fieldtype": "Data",
#             "width": 340,
#         },
#         {
#             "fieldname": "monthly_credit",
#             "label": _("For the Month Receipt"),
#             "fieldtype": "Currency",
#             "width": 150,
#         },
#         {
#             "fieldname": "annually_credit",
#             "label": _("Annual Progressive Receipt"),
#             "fieldtype": "Currency",
#             "width": 170,
#         },
#         {
#             "fieldname": "monthly_debit",
#             "label": _("For The Month Payment"),
#             "fieldtype": "Currency",
#             "width": 150,
#         },
#         {
#             "fieldname": "anually_debit",
#             "label": _("Annual Progressive Payment"),
#             "fieldtype": "Currency",
#             "width": 170,
#         },
#     ]


# def get_data(filters):
#     conditions = [
#         "gle.company = %(company)s",
#         "gle.posting_date BETWEEN %(year_start)s AND %(progressive_end)s",
#         "gle.is_cancelled = 0",
#         "acc.company = %(company)s",
#     ]

#     if not filters.with_period_closing_entry:
#         conditions.extend([
#             "COALESCE(gle.is_opening, '') != 'Yes'",
#             "COALESCE(gle.voucher_type, '') != 'Period Closing Voucher'",
#         ])

#     account_filter = ""
#     if filters.get("account"):
#         account_filter = """
#             AND (
#                 acc.name = %(account)s
#                 OR (
#                     acc.lft >= selected.lft
#                     AND acc.rgt <= selected.rgt
#                 )
#             )
#         """

#     selected_join = ""
#     if filters.get("account"):
#         selected_join = """
#             INNER JOIN `tabAccount` selected
#                 ON selected.name = %(account)s
#         """

#     gl_rows = frappe.db.sql(
#         f"""
#         SELECT
#             acc.name AS account,
#             acc.parent_account,
#             acc.is_group,
#             acc.lft,
#             acc.rgt,

#             SUM(
#                 CASE
#                     WHEN gle.posting_date BETWEEN
#                         %(month_start)s AND %(month_end)s
#                     THEN gle.credit ELSE 0
#                 END
#             ) AS mcredit,

#             SUM(gle.credit) AS credit,

#             SUM(
#                 CASE
#                     WHEN gle.posting_date BETWEEN
#                         %(month_start)s AND %(month_end)s
#                     THEN gle.debit ELSE 0
#                 END
#             ) AS mdebit,

#             SUM(gle.debit) AS debit

#         FROM `tabGL Entry` gle
#         INNER JOIN `tabAccount` acc
#             ON acc.name = gle.account
#         {selected_join}
#         WHERE {" AND ".join(conditions)}
#             {account_filter}
#         GROUP BY
#             acc.name, acc.parent_account, acc.is_group,
#             acc.lft, acc.rgt
#         """,
#         filters,
#         as_dict=True,
#     )

#     # Load the complete account tree for the selected company.
#         # Load the complete account tree for the selected company.
#     account_accounts = frappe.get_all(
#         "Account",
#         filters={"company": filters.company},
#         fields=[
#             "name",
#             "account_number",
#             "parent_account",
#             "is_group",
#             "lft",
#             "rgt",
#         ],
#         order_by="lft ASC",
#     )
 

#     account_map = {a.name: a for a in account_accounts}

#     # Initialize totals for every account.
#     totals = {
#         account.name: {
#             "mcredit": 0.0,
#             "credit": 0.0,
#             "mdebit": 0.0,
#             "debit": 0.0,
#         }
#         for account in account_accounts
#     }

#     # Assign GL totals to each account.
#     for row in gl_rows:
#         if row.account in totals:
#             totals[row.account] = {
#                 "mcredit": flt(row.mcredit),
#                 "credit": flt(row.credit),
#                 "mdebit": flt(row.mdebit),
#                 "debit": flt(row.debit),
#             }

#     # Roll child totals up into their parents.
#     for account in sorted(
#         account_accounts,
#         key=lambda a: a.lft,
#         reverse=True,
#     ):
#         parent = account.parent_account

#         if parent and parent in totals:
#             for field in ("mcredit", "credit", "mdebit", "debit"):
#                 totals[parent][field] += totals[account.name][field]

    
#     top_level_accounts = [
#         account
#         for account in account_accounts
#         if not account.parent_account
#         and str(account.account_number or "").isdigit()
#         and 2 <= int(account.account_number) <= 10
#     ]

#     # Sort roots numerically: 2, 3, 4, ..., 10.
#     top_level_accounts.sort(
#         key=lambda account: int(account.account_number)
#     )

#     # Append each root and its descendants in hierarchy order.
#     accounts = []

#     for root in top_level_accounts:
#         descendants = [
#             account
#             for account in account_accounts
#             if root.lft <= account.lft
#             and account.rgt <= root.rgt
#         ]
#         accounts.extend(descendants)

#     # Optional account filter: show the selected account and descendants.
#     selected = account_map.get(filters.get("account"))

#     if selected:
#         accounts = [
#             account
#             for account in accounts
#             if account.lft >= selected.lft
#             and account.rgt <= selected.rgt
#         ]

#     # Build report rows.
#     data = []

#     for account in accounts:
#         amount = totals[account.name]

#         # Hide empty ledger accounts, but retain group accounts.
#         if not account.is_group and not any(amount.values()):
#             continue

#         data.append({
#             "account": account.name,
#             "indent": max(
#                 0,
#                 sum(
#                     1
#                     for parent in accounts
#                     if parent.is_group
#                     and parent.lft < account.lft
#                     and parent.rgt > account.rgt
#                 ),
#             ),
#             "parent_account": account.parent_account,
#             "is_group": account.is_group,
#             "mcredit": amount["mcredit"],
#             "credit": amount["credit"],
#             "mdebit": amount["mdebit"],
#             "debit": amount["debit"],
#         })
#     opening_balance_rows = [{
#         "account": "Opening Balance",
#         "indent": 0,
#         "is_group": 1,
#         "mcredit": 0.0,
#         "credit": 0.0,
#         "mdebit": 0.0,
#         "debit": 0.0,
#     }]

#     # Define the desired account hierarchy.
#     opening_balance_groups = [
#         {
#             "parent": "12 a - Cash - RBA",
#             "children": [
#                 "80.01 - Cash Transactions - RBA",
#             ],
#         },
#         {
#             "parent": "12 b - Bank - RBA",
#             "children": [
#                 "80.02 - Bank Transactions - RBA",

#             ],
#                "against": "Temporary Account Bank - RBA",
#         },
#     ]

#     for group in opening_balance_groups:
#         parent = frappe.db.get_value(
#             "Account",
#             {
#                 "name": group["parent"],
#                 "company": filters.company,
#             },
#             "name",
#         )

#         if not parent:
#             continue

#         account_names = [parent] + group["children"]

#         # Conditions apply only to the Cash/Bank opening balance section.
#         opening_conditions = [
#             "company = %(company)s",
#             "account IN %(accounts)s",
#             "is_opening = 'Yes'",
#             "is_cancelled = 0",
#             "posting_date BETWEEN %(start_date)s AND %(end_date)s",
#         ]

#         # Apply this additional condition only to Bank.
#         if group.get("against"):
#             opening_conditions.append("against = %(against)s")

#         opening_filters = {
#             "company": filters.company,
#             "accounts": tuple(account_names),
#             "start_date": filters.year_start,
#             "end_date": filters.progressive_end,
#         }

#         if group.get("against"):
#             opening_filters["against"] = group["against"]

#         opening_totals = frappe.db.sql(
#             f"""
#             SELECT
#                 account,
#                 SUM(credit) AS credit,
#                 SUM(debit) AS debit
#             FROM `tabGL Entry`
#             WHERE {" AND ".join(opening_conditions)}
#             GROUP BY account
#             """,
#             opening_filters,
#             as_dict=True,
#         )

#         amounts = {
#             row.account: {
#                 "credit": flt(row.credit),
#                 "debit": flt(row.debit),
#             }
#             for row in opening_totals
#         }

#         # Calculate the parent total from its opening entries.
#         parent_credit = sum(
#             amounts.get(name, {}).get("credit", 0.0)
#             for name in account_names
#         )
#         parent_debit = sum(
#             amounts.get(name, {}).get("debit", 0.0)
#             for name in account_names
#         )

#         opening_balance_rows.append({
#             "account": parent,
#             "indent": 1,
#             "is_group": 1,
#             "mcredit": 0.0,
#             "credit": parent_credit,
#             "mdebit": 0.0,
#             "debit": parent_debit,
#         })

#         # Display the individual Cash/Bank transaction account.
#         for child_name in group["children"]:
#             child = frappe.db.get_value(
#                 "Account",
#                 {
#                     "name": child_name,
#                     "company": filters.company,
#                 },
#                 "name",
#             )

#             if not child:
#                 continue

#             child_amount = amounts.get(child, {})

#             opening_balance_rows.append({
#                 "account": child,
#                 "indent": 2,
#                 "is_group": 0,
#                 "mcredit": 0.0,
#                 "credit": flt(child_amount.get("credit", 0.0)),
#                 "mdebit": 0.0,
#                 "debit": flt(child_amount.get("debit", 0.0)),
#             })

#     # Place Opening Balance at the beginning of the report.
#     data = opening_balance_rows + data

#     return data

# import frappe
# from frappe import _
# from frappe.utils import flt


# def execute(filters=None):
#     filters = frappe._dict(filters or {})
#     validate_filters(filters)

#     columns = get_columns()
#     data = get_data(filters)

#     return columns, data


# def validate_filters(filters):
#     for field in ("company", "fiscal_year", "month"):
#         if not filters.get(field):
#             frappe.throw(
#                 _("Please select {0}").format(
#                     field.replace("_", " ").title()
#                 )
#             )

#     if not frappe.db.exists("Company", filters.company):
#         frappe.throw(_("Invalid Company"))

#     if not frappe.db.exists("Fiscal Year", filters.fiscal_year):
#         frappe.throw(_("Invalid Fiscal Year"))

#     month_map = {
#         "Jan": 1,
#         "Feb": 2,
#         "Mar": 3,
#         "Apr": 4,
#         "May": 5,
#         "Jun": 6,
#         "Jul": 7,
#         "Aug": 8,
#         "Sep": 9,
#         "Oct": 10,
#         "Nov": 11,
#         "Dec": 12,
#     }

#     filters.month_number = month_map.get(filters.month)

#     if not filters.month_number:
#         frappe.throw(_("Please select a valid month"))

#     # Fiscal year assumed to run from July through June.
#     filters.progressive_month = (
#         (filters.month_number - 7) % 12
#     ) + 1


# def get_columns():
#     return [
#         {
#             "fieldname": "account",
#             "label": _("Group/Broad Head Of Account"),
#             "fieldtype": "Data",
#             "width": 340,
#         },
#         {
#             "fieldname": "monthly_credit",
#             "label": _("For the Month Receipt"),
#             "fieldtype": "Currency",
#             "width": 150,
#         },
#         {
#             "fieldname": "annually_credit",
#             "label": _("Annual Progressive Receipt"),
#             "fieldtype": "Currency",
#             "width": 170,
#         },
#         {
#             "fieldname": "monthly_debit",
#             "label": _("For The Month Payment"),
#             "fieldtype": "Currency",
#             "width": 150,
#         },
#         {
#             "fieldname": "anually_debit",
#             "label": _("Annual Progressive Payment"),
#             "fieldtype": "Currency",
#             "width": 170,
#         },
#     ]


# def get_data(filters):
#     conditions = [
#         "gle.company = %(company)s",
#         "gle.fiscal_year = %(fiscal_year)s",
#         "gle.is_cancelled = 0",
#         "acc.company = %(company)s",
#         "COALESCE(gle.is_opening, '') != 'Yes'",
#         "COALESCE(gle.voucher_type, '') != 'Period Closing Voucher'",
#     ]

#     account_filter = ""
#     selected_join = ""

#     if filters.get("account"):
#         account_filter = """
#             AND (
#                 acc.name = %(account)s
#                 OR (
#                     acc.lft >= selected.lft
#                     AND acc.rgt <= selected.rgt
#                 )
#             )
#         """
#         selected_join = """
#             INNER JOIN `tabAccount` selected
#                 ON selected.name = %(account)s
#         """

#     gl_rows = frappe.db.sql(
#         f"""
#         SELECT
#             acc.name AS account,
#             acc.parent_account,
#             acc.is_group,
#             acc.lft,
#             acc.rgt,

#             SUM(
#                 CASE
#                     WHEN MONTH(gle.posting_date) = %(month_number)s
#                     THEN gle.credit
#                     ELSE 0
#                 END
#             ) AS monthly_credit,

#             SUM(
#                 CASE
#                     WHEN gle.fiscal_year = %(fiscal_year)s
#                         AND MONTH(gle.posting_date) <= %(month_number)s
#                         THEN gle.credit
#                     ELSE 0
#                 END
#             ) AS annually_credit,

#             SUM(
#                 CASE
#                     WHEN MONTH(gle.posting_date) = %(month_number)s
#                     THEN gle.debit
#                     ELSE 0
#                 END
#             ) AS monthly_debit,

#             SUM(
#                 CASE
#                     WHEN gle.fiscal_year = %(fiscal_year)s
#                     AND MONTH(gle.posting_date) <= %(month_number)s
#                     THEN gle.debit
#                     ELSE 0
#                 END
#             ) AS anually_debit

#         FROM `tabGL Entry` gle

#         INNER JOIN `tabAccount` acc
#             ON acc.name = gle.account

#         {selected_join}

#         WHERE {" AND ".join(conditions)}
#             {account_filter}

#         GROUP BY
#             acc.name,
#             acc.parent_account,
#             acc.is_group,
#             acc.lft,
#             acc.rgt
#         """,
#         filters,
#         as_dict=True,
#     )

#     account_accounts = frappe.get_all(
#         "Account",
#         filters={"company": filters.company},
#         fields=[
#             "name",
#             "account_number",
#             "parent_account",
#             "is_group",
#             "lft",
#             "rgt",
#         ],
#         order_by="lft ASC",
#     )

#     account_map = {
#         account.name: account
#         for account in account_accounts
#     }

#     fields = (
#         "monthly_credit",
#         "annually_credit",
#         "monthly_debit",
#         "anually_debit",
#     )

#     totals = {
#         account.name: {
#             field: 0.0
#             for field in fields
#         }
#         for account in account_accounts
#     }

#     for row in gl_rows:
#         if row.account in totals:
#             for field in fields:
#                 totals[row.account][field] = flt(row.get(field))

#     # Roll child account totals into parent accounts.
#     for account in sorted(
#         account_accounts,
#         key=lambda item: item.lft,
#         reverse=True,
#     ):
#         parent = account.parent_account

#         if parent and parent in totals:
#             for field in fields:
#                 totals[parent][field] += totals[account.name][field]

#     # Get top-level accounts numbered 2 through 10.
#     top_level_accounts = [
#         account
#         for account in account_accounts
#         if not account.parent_account
#         and str(account.account_number or "").isdigit()
#         and 2 <= int(account.account_number) <= 10
#     ]

#     top_level_accounts.sort(
#         key=lambda account: int(account.account_number)
#     )

#     accounts = []

#     for root in top_level_accounts:
#         accounts.extend(
#             account
#             for account in account_accounts
#             if root.lft <= account.lft
#             and account.rgt <= root.rgt
#         )

#     # Apply optional account filter.
#     selected = account_map.get(filters.get("account"))

#     if selected:
#         accounts = [
#             account
#             for account in accounts
#             if account.lft >= selected.lft
#             and account.rgt <= selected.rgt
#         ]

#     data = []

#     for account in accounts:
#         amount = totals[account.name]

#         if not account.is_group and not any(
#             flt(amount[field]) for field in fields
#         ):
#             continue

#         indent = 0
#         parent = account.parent_account

#         while parent and parent in account_map:
#             indent += 1
#             parent = account_map[parent].parent_account

#         data.append({
#             "account": account.name,
#             "indent": indent,
#             "is_group": account.is_group,
#             "monthly_credit": flt(amount["monthly_credit"]),
#             "annually_credit": flt(amount["annually_credit"]),
#             "monthly_debit": flt(amount["monthly_debit"]),
#             "anually_debit": flt(amount["anually_debit"]),
#         })

#     # Opening Balance section: Cash and Bank.
#     opening_balance_rows = [{
#         "account": _("Opening Balance"),
#         "indent": 0,
#         "is_group": 1,
#         "monthly_credit": 0.0,
#         "annually_credit": 0.0,
#         "monthly_debit": 0.0,
#         "anually_debit": 0.0,
#     }]

#     opening_balance_groups = [
#         {
#             "parent": "12 a - Cash - RBA",
#             "children": ["80.01 - Cash Transactions - RBA"],
#         },
#         {
#             "parent": "12 b - Bank - RBA",
#             "children": ["80.02 - Bank Transactions - RBA"],
#             "against": "Temporary Account Bank - RBA",
#         },
#     ]

#     for group in opening_balance_groups:
#         parent_name = group["parent"]
#         child_names = group["children"]

#         existing_children = [
#             child
#             for child in child_names
#             if frappe.db.exists(
#                 "Account",
#                 {
#                     "name": child,
#                     "company": filters.company,
#                 },
#             )
#         ]

#         if not existing_children:
#             continue

#         opening_conditions = [
#             "company = %(company)s",
#             "fiscal_year = %(fiscal_year)s",
#             "account IN %(accounts)s",
#             "is_opening = 'Yes'",
#             "is_cancelled = 0",
#         ]

#         opening_params = {
#             "company": filters.company,
#             "fiscal_year": filters.fiscal_year,
#             "accounts": tuple(existing_children),
#         }

#         if group.get("against"):
#             opening_conditions.append("against = %(against)s")
#             opening_params["against"] = group["against"]

#         opening_rows = frappe.db.sql(
#             f"""
#             SELECT
#                 account,
#                 SUM(debit) AS debit,
#                 SUM(credit) AS credit
#             FROM `tabGL Entry`
#             WHERE {" AND ".join(opening_conditions)}
#             GROUP BY account
#             """,
#             opening_params,
#             as_dict=True,
#         )

#         opening_map = {
#             row.account: row
#             for row in opening_rows
#         }

#         parent_debit = 0.0
#         parent_credit = 0.0

#         child_rows = []

#         for child_name in existing_children:
#             row = opening_map.get(child_name)

#             debit = flt(row.debit) if row else 0.0
#             credit = flt(row.credit) if row else 0.0

#             parent_debit += debit
#             parent_credit += credit

#             child_rows.append({
#                 "account": child_name,
#                 "indent": 2,
#                 "is_group": 0,
#                 "monthly_credit": max(debit - credit, 0.0),
#                 "annually_credit": max(debit - credit, 0.0),
#                 "monthly_debit": max(credit - debit, 0.0),
#                 "anually_debit": max(credit - debit, 0.0),
#             })

#         parent_exists = frappe.db.exists(
#             "Account",
#             {
#                 "name": parent_name,
#                 "company": filters.company,
#             },
#         )

#         if not parent_exists:
#             continue

#         opening_balance_rows.append({
#             "account": parent_name,
#             "indent": 1,
#             "is_group": 1,
#             "monthly_credit": max(parent_debit - parent_credit, 0.0),
#             "annually_credit": max(parent_debit - parent_credit, 0.0),
#             "monthly_debit":  max(parent_credit - parent_debit, 0.0),
#             "anually_debit": max(parent_credit - parent_debit, 0.0),
#         })

#         opening_balance_rows.extend(child_rows)

#     return opening_balance_rows + data

# import frappe
# from frappe import _
# from frappe.utils import flt


# def execute(filters=None):
#     filters = frappe._dict(filters or {})
#     validate_filters(filters)

#     columns = get_columns()
#     data = get_data(filters)

#     return columns, data


# def validate_filters(filters):
#     for field in ("company", "fiscal_year", "month"):
#         if not filters.get(field):
#             frappe.throw(
#                 _("Please select {0}").format(
#                     field.replace("_", " ").title()
#                 )
#             )

#     if not frappe.db.exists("Company", filters.company):
#         frappe.throw(_("Invalid Company"))

#     if not frappe.db.exists("Fiscal Year", filters.fiscal_year):
#         frappe.throw(_("Invalid Fiscal Year"))

#     month_map = {
#         "Jan": 1,
#         "Feb": 2,
#         "Mar": 3,
#         "Apr": 4,
#         "May": 5,
#         "Jun": 6,
#         "Jul": 7,
#         "Aug": 8,
#         "Sep": 9,
#         "Oct": 10,
#         "Nov": 11,
#         "Dec": 12,
#     }

#     filters.month_number = month_map.get(filters.month)

#     if not filters.month_number:
#         frappe.throw(_("Please select a valid month"))

#     # Fiscal year runs from July through June.
#     filters.progressive_month = (
#         (filters.month_number - 7) % 12
#     ) + 1


# def get_columns():
#     return [
#         {
#             "fieldname": "account",
#             "label": _("Group/Broad Head Of Account"),
#             "fieldtype": "Data",
#             "width": 340,
#         },
#         {
#             "fieldname": "monthly_credit",
#             "label": _("For the Month Receipt"),
#             "fieldtype": "Currency",
#             "width": 150,
#         },
#         {
#             "fieldname": "annually_credit",
#             "label": _("Annual Progressive Receipt"),
#             "fieldtype": "Currency",
#             "width": 170,
#         },
#         {
#             "fieldname": "monthly_debit",
#             "label": _("For The Month Payment"),
#             "fieldtype": "Currency",
#             "width": 150,
#         },
#         {
#             "fieldname": "anually_debit",
#             "label": _("Annual Progressive Payment"),
#             "fieldtype": "Currency",
#             "width": 170,
#         },
#     ]


# def get_data(filters):
#     conditions = [
#         "gle.company = %(company)s",
#         "gle.fiscal_year = %(fiscal_year)s",
#         "gle.is_cancelled = 0",
#         "acc.company = %(company)s",
#         "COALESCE(gle.is_opening, '') != 'Yes'",
#         "COALESCE(gle.voucher_type, '') != 'Period Closing Voucher'",
#     ]

#     account_filter = ""
#     selected_join = ""

#     if filters.get("account"):
#         account_filter = """
#             AND (
#                 acc.name = %(account)s
#                 OR (
#                     acc.lft >= selected.lft
#                     AND acc.rgt <= selected.rgt
#                 )
#             )
#         """

#         selected_join = """
#             INNER JOIN `tabAccount` selected
#                 ON selected.name = %(account)s
#         """

#     # Normal GL transactions.
#     # Monthly totals use the selected calendar month.
#     # Annual progressive totals follow the July-June fiscal year.
#     gl_rows = frappe.db.sql(
#         f"""
#         SELECT
#             acc.name AS account,
#             acc.parent_account,
#             acc.is_group,
#             acc.lft,
#             acc.rgt,

#             SUM(
#                 CASE
#                     WHEN MONTH(gle.posting_date) = %(month_number)s
#                     THEN gle.credit
#                     ELSE 0
#                 END
#             ) AS monthly_credit,

#             SUM(
#                 CASE
#                     WHEN (
#                         MOD(MONTH(gle.posting_date) - 7 + 12, 12) + 1
#                     ) <= %(progressive_month)s
#                     THEN gle.credit
#                     ELSE 0
#                 END
#             ) AS annually_credit,

#             SUM(
#                 CASE
#                     WHEN MONTH(gle.posting_date) = %(month_number)s
#                     THEN gle.debit
#                     ELSE 0
#                 END
#             ) AS monthly_debit,

#             SUM(
#                 CASE
#                     WHEN (
#                         MOD(MONTH(gle.posting_date) - 7 + 12, 12) + 1
#                     ) <= %(progressive_month)s
#                     THEN gle.debit
#                     ELSE 0
#                 END
#             ) AS anually_debit

#         FROM `tabGL Entry` gle

#         INNER JOIN `tabAccount` acc
#             ON acc.name = gle.account

#         {selected_join}

#         WHERE {" AND ".join(conditions)}
#             {account_filter}

#         GROUP BY
#             acc.name,
#             acc.parent_account,
#             acc.is_group,
#             acc.lft,
#             acc.rgt
#         """,
#         filters,
#         as_dict=True,
#     )

#     account_accounts = frappe.get_all(
#         "Account",
#         filters={"company": filters.company},
#         fields=[
#             "name",
#             "account_number",
#             "parent_account",
#             "is_group",
#             "lft",
#             "rgt",
#         ],
#         order_by="lft ASC",
#     )

#     account_map = {
#         account.name: account
#         for account in account_accounts
#     }

#     fields = (
#         "monthly_credit",
#         "annually_credit",
#         "monthly_debit",
#         "anually_debit",
#     )

#     totals = {
#         account.name: {
#             field: 0.0
#             for field in fields
#         }
#         for account in account_accounts
#     }

#     for row in gl_rows:
#         if row.account in totals:
#             for field in fields:
#                 totals[row.account][field] = flt(row.get(field))

#     # Roll child account totals into parent accounts.
#     for account in sorted(
#         account_accounts,
#         key=lambda item: item.lft,
#         reverse=True,
#     ):
#         parent = account.parent_account

#         if parent and parent in totals:
#             for field in fields:
#                 totals[parent][field] += totals[account.name][field]

#     # Get top-level accounts numbered 2 through 10.
#     top_level_accounts = [
#         account
#         for account in account_accounts
#         if not account.parent_account
#         and str(account.account_number or "").isdigit()
#         and 2 <= int(account.account_number) <= 10
#     ]

#     top_level_accounts.sort(
#         key=lambda account: int(account.account_number)
#     )

#     accounts = []

#     for root in top_level_accounts:
#         accounts.extend(
#             account
#             for account in account_accounts
#             if root.lft <= account.lft
#             and account.rgt <= root.rgt
#         )

#     # Apply optional account filter.
#     selected = account_map.get(filters.get("account"))

#     if selected:
#         accounts = [
#             account
#             for account in accounts
#             if account.lft >= selected.lft
#             and account.rgt <= selected.rgt
#         ]

#     data = []

#     for account in accounts:
#         amount = totals[account.name]

#         if not account.is_group and not any(
#             flt(amount[field]) for field in fields
#         ):
#             continue

#         indent = 0
#         parent = account.parent_account

#         while parent and parent in account_map:
#             indent += 1
#             parent = account_map[parent].parent_account

#         data.append({
#             "account": account.name,
#             "indent": indent,
#             "is_group": account.is_group,
#             "monthly_credit": flt(amount["monthly_credit"]),
#             "annually_credit": flt(amount["annually_credit"]),
#             "monthly_debit": flt(amount["monthly_debit"]),
#             "anually_debit": flt(amount["anually_debit"]),
#         })

#     # ---------------------------------------------------------
#     # Opening Balance section: Cash and Bank
#     # ---------------------------------------------------------

#     opening_balance_rows = [{
#         "account": _("Opening Balance"),
#         "indent": 0,
#         "is_group": 1,
#         "monthly_credit": 0.0,
#         "annually_credit": 0.0,
#         "monthly_debit": 0.0,
#         "anually_debit": 0.0,
#     }]

#     opening_balance_groups = [
#         {
#             "parent": "12 a - Cash - RBA",
#             "children": [
#                 "80.01 - Cash Transactions - RBA"
#             ],
#         },
#         {
#             "parent": "12 b - Bank - RBA",
#             "children": [
#                 "80.02 - Bank Transactions - RBA"
#             ],
#             "against": "Temporary Account Bank - RBA",
#         },
#     ]

#     for group in opening_balance_groups:
#         parent_name = group["parent"]
#         child_names = group["children"]

#         existing_children = [
#             child
#             for child in child_names
#             if frappe.db.exists(
#                 "Account",
#                 {
#                     "name": child,
#                     "company": filters.company,
#                 },
#             )
#         ]

#         if not existing_children:
#             continue

#         opening_conditions = [
#             "company = %(company)s",
#             "fiscal_year = %(fiscal_year)s",
#             "account IN %(accounts)s",
#             "is_opening = 'Yes'",
#             "is_cancelled = 0",
#         ]

#         opening_params = {
#             "company": filters.company,
#             "fiscal_year": filters.fiscal_year,
#             "accounts": tuple(existing_children),
#         }

#         if group.get("against"):
#             opening_conditions.append(
#                 "against = %(against)s"
#             )
#             opening_params["against"] = group["against"]

#         # Group opening entries by account and posting month.
#         opening_rows = frappe.db.sql(
#             f"""
#             SELECT
#                 account,
#                 MONTH(posting_date) AS opening_month,
#                 SUM(debit) AS debit,
#                 SUM(credit) AS credit
#             FROM `tabGL Entry`
#             WHERE {" AND ".join(opening_conditions)}
#             GROUP BY account, MONTH(posting_date)
#             """,
#             opening_params,
#             as_dict=True,
#         )

#         opening_map = {}

#         for row in opening_rows:
#             opening_map.setdefault(
#                 row.account, []
#             ).append(row)

#         parent_debit = 0.0
#         parent_credit = 0.0
#         parent_monthly_credit = 0.0
#         parent_monthly_debit = 0.0

#         child_rows = []

#         for child_name in existing_children:
#             rows = opening_map.get(child_name, [])

#             debit = sum(
#                 flt(row.debit)
#                 for row in rows
#             )

#             credit = sum(
#                 flt(row.credit)
#                 for row in rows
#             )

#             # Show opening amounts in monthly columns only
#             # when the selected month matches their posting month.
#             monthly_credit_balance = sum(
#                 max(
#                     flt(row.credit) - flt(row.debit),
#                     0.0,
#                 )
#                 for row in rows
#                 if row.opening_month == filters.month_number
#             )

#             monthly_debit_balance = sum(
#                 max(
#                     flt(row.debit) - flt(row.credit),
#                     0.0,
#                 )
#                 for row in rows
#                 if row.opening_month == filters.month_number
#             )

#             parent_debit += debit
#             parent_credit += credit
#             parent_monthly_credit += monthly_credit_balance
#             parent_monthly_debit += monthly_debit_balance

#             child_rows.append({
#                 "account": child_name,
#                 "indent": 2,
#                 "is_group": 0,
#                 "monthly_credit": monthly_credit_balance,
#                 "annually_credit": max(
#                     debit - credit, 0.0
#                 ),
#                 "monthly_debit": monthly_debit_balance,
#                 "anually_debit": max(
#                     credit - debit, 0.0
#                 ),
#             })

            

#         parent_exists = frappe.db.exists(
#             "Account",
#             {
#                 "name": parent_name,
#                 "company": filters.company,
#             },
#         )

#         if not parent_exists:
#             continue

#         opening_balance_rows.append({
#             "account": parent_name,
#             "indent": 1,
#             "is_group": 1,
#             "monthly_credit": parent_monthly_credit,
#             "annually_credit": max(
#                 parent_debit - parent_credit, 0.0
#             ),
#             "monthly_debit": parent_monthly_debit,
#             "anually_debit": max(
#                 parent_credit - parent_debit, 0.0
#             ),
#         })

#         opening_balance_rows.extend(child_rows)

#     return opening_balance_rows + data



import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    filters = frappe._dict(filters or {})
    validate_filters(filters)

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def validate_filters(filters):
    for field in ("company", "fiscal_year", "month"):
        if not filters.get(field):
            frappe.throw(
                _("Please select {0}").format(
                    field.replace("_", " ").title()
                )
            )

    if not frappe.db.exists("Company", filters.company):
        frappe.throw(_("Invalid Company"))

    if not frappe.db.exists("Fiscal Year", filters.fiscal_year):
        frappe.throw(_("Invalid Fiscal Year"))

    month_map = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
    }

    filters.month_number = month_map.get(filters.month)

    if not filters.month_number:
        frappe.throw(_("Please select a valid month"))

    # Fiscal year runs from July through June.
    filters.progressive_month = (
        (filters.month_number - 7) % 12
    ) + 1


def get_columns():
    return [
        {
            "fieldname": "account",
            "label": _("Group/Broad Head Of Account"),
            "fieldtype": "Data",
            "width": 340,
        },
        {
            "fieldname": "monthly_credit",
            "label": _("For the Month Receipt"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "annually_credit",
            "label": _("Annual Progressive Receipt"),
            "fieldtype": "Currency",
            "width": 170,
        },
        {
            "fieldname": "monthly_debit",
            "label": _("For The Month Payment"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "anually_debit",
            "label": _("Annual Progressive Payment"),
            "fieldtype": "Currency",
            "width": 170,
        },
    ]


def get_data(filters):
    conditions = [
        "gle.company = %(company)s",
        "gle.fiscal_year = %(fiscal_year)s",
        "gle.is_cancelled = 0",
        "acc.company = %(company)s",
        "COALESCE(gle.is_opening, '') != 'Yes'",
        "COALESCE(gle.voucher_type, '') != 'Period Closing Voucher'",
    ]

    account_filter = ""
    selected_join = ""

    if filters.get("account"):
        account_filter = """
            AND (
                acc.name = %(account)s
                OR (
                    acc.lft >= selected.lft
                    AND acc.rgt <= selected.rgt
                )
            )
        """

        selected_join = """
            INNER JOIN `tabAccount` selected
                ON selected.name = %(account)s
        """

    # Normal GL transactions.
    # Monthly totals use the selected calendar month.
    # Annual progressive totals follow the July-June fiscal year.
    gl_rows = frappe.db.sql(
        f"""
        SELECT
            acc.name AS account,
            acc.parent_account,
            acc.is_group,
            acc.lft,
            acc.rgt,

            SUM(
                CASE
                    WHEN MONTH(gle.posting_date) = %(month_number)s
                    THEN gle.credit
                    ELSE 0
                END
            ) AS monthly_credit,

            SUM(
                CASE
                    WHEN 
                        gle.fiscal_year = %(fiscal_year)s 
                    
                    THEN gle.credit
                    ELSE 0
                END
            ) AS annually_credit,

            SUM(
                CASE
                    WHEN MONTH(gle.posting_date) = %(month_number)s
                    THEN gle.debit
                    ELSE 0
                END
            ) AS monthly_debit,

            SUM(
                CASE
                    WHEN  
                        gle.fiscal_year = %(fiscal_year)s 
                    THEN gle.debit
                    ELSE 0
                END
            ) AS anually_debit

        FROM `tabGL Entry` gle

        INNER JOIN `tabAccount` acc
            ON acc.name = gle.account

        {selected_join}

        WHERE {" AND ".join(conditions)}
            {account_filter}

        GROUP BY
            acc.name,
            acc.parent_account,
            acc.is_group,
            acc.lft,
            acc.rgt
        """,
        filters,
        as_dict=True,
    )

    account_accounts = frappe.get_all(
        "Account",
        filters={"company": filters.company},
        fields=[
            "name",
            "account_number",
            "parent_account",
            "is_group",
            "lft",
            "rgt",
        ],
        order_by="lft ASC",
    )

    account_map = {
        account.name: account
        for account in account_accounts
    }

    fields = (
        "monthly_credit",
        "annually_credit",
        "monthly_debit",
        "anually_debit",
    )

    totals = {
        account.name: {
            field: 0.0
            for field in fields
        }
        for account in account_accounts
    }

    for row in gl_rows:
        if row.account in totals:
            for field in fields:
                totals[row.account][field] = flt(row.get(field))

    # Roll child account totals into parent accounts.
    for account in sorted(
        account_accounts,
        key=lambda item: item.lft,
        reverse=True,
    ):
        parent = account.parent_account

        if parent and parent in totals:
            for field in fields:
                totals[parent][field] += totals[account.name][field]

    # Get top-level accounts numbered 2 through 10.
    top_level_accounts = [
        account
        for account in account_accounts
        if not account.parent_account
        and str(account.account_number or "").isdigit()
        and 2 <= int(account.account_number) <= 10
    ]

    top_level_accounts.sort(
        key=lambda account: int(account.account_number)
    )

    accounts = []

    for root in top_level_accounts:
        accounts.extend(
            account
            for account in account_accounts
            if root.lft <= account.lft
            and account.rgt <= root.rgt
        )

    # Apply optional account filter.
    selected = account_map.get(filters.get("account"))

    if selected:
        accounts = [
            account
            for account in accounts
            if account.lft >= selected.lft
            and account.rgt <= selected.rgt
        ]

    data = []

    for account in accounts:
        amount = totals[account.name]

        if not account.is_group and not any(
            flt(amount[field]) for field in fields
        ):
            continue

        indent = 0
        parent = account.parent_account

        while parent and parent in account_map:
            indent += 1
            parent = account_map[parent].parent_account

        data.append({
            "account": account.name,
            "indent": indent,
            "is_group": account.is_group,
            "monthly_credit": flt(amount["monthly_credit"]),
            "annually_credit": flt(amount["annually_credit"]),
            "monthly_debit": flt(amount["monthly_debit"]),
            "anually_debit": flt(amount["anually_debit"]),
        })

    # ---------------------------------------------------------
    # Opening Balance section: Cash and Bank
    # Opening amounts are displayed in Receipt columns.
    # ---------------------------------------------------------

    opening_balance_rows = [{
        "account": _("Opening Balance"),
        "indent": 0,
        "is_group": 1,
        "monthly_credit": 0.0,
        "annually_credit": 0.0,
        "monthly_debit": 0.0,
        "anually_debit": 0.0,
    }]

    opening_balance_groups = [
        {
            "label": "Cash",
            "parent": "12 a - Cash - RBA",
            "children": [
                "80.01 - Cash Transactions - RBA"
            ],
        },
        { 
            "label": "Bank",
            "parent": "12 b - Bank - RBA",
            "children": [
                "80.02 - Bank Transactions - RBA"
            ],
            "against": "Temporary Account Bank - RBA",
        },
    ]

    for group in opening_balance_groups:
        parent_name = group["parent"]
        child_names = group["children"]

        existing_children = [
            child
            for child in child_names
            if frappe.db.exists(
                "Account",
                {
                    "name": child,
                    "company": filters.company,
                },
            )
        ]

        parent_exists = frappe.db.exists(
            "Account",
            {
                "name": parent_name,
                "company": filters.company,
            },
        )

        if not parent_exists or not existing_children:
            continue

        opening_conditions = [
            "company = %(company)s",
            "fiscal_year = %(fiscal_year)s",
            "account IN %(accounts)s",
            "is_opening = 'Yes'",
            "is_cancelled = 0",
        ]

        opening_params = {
            "company": filters.company,
            "fiscal_year": filters.fiscal_year,
            "accounts": tuple(existing_children),
        }

        if group.get("against"):
            opening_conditions.append(
                "against = %(against)s"
            )
            opening_params["against"] = group["against"]

        # Group opening entries by account and posting month.
        opening_rows = frappe.db.sql(
            f"""
            SELECT
                account,
                MONTH(posting_date) AS opening_month,
                SUM(debit) AS debit,
                SUM(credit) AS credit
            FROM `tabGL Entry`
            WHERE {" AND ".join(opening_conditions)}
            GROUP BY account, MONTH(posting_date)
            """,
            opening_params,
            as_dict=True,
        )

        opening_map = {}

        for row in opening_rows:
            opening_map.setdefault(
                row.account, []
            ).append(row)

        parent_annual_receipt = 0.0
        parent_monthly_receipt = 0.0

        child_rows = []

        for child_name in existing_children:
            rows = opening_map.get(child_name, [])

            total_debit = sum(
                flt(row.debit)
                for row in rows
            )

            total_credit = sum(
                flt(row.credit)
                for row in rows
            )

            # Net debit opening balance displayed as a receipt.
            annual_receipt = max(
                total_debit - total_credit,
                0.0,
            )

            # Monthly receipt appears only in the selected
            # month when the opening entry was posted.
            monthly_receipt = sum(
                max(
                    flt(row.debit) - flt(row.credit),
                    0.0,
                )
                for row in rows
                if row.opening_month == filters.month_number
            )

            parent_annual_receipt += annual_receipt
            parent_monthly_receipt += monthly_receipt

            child_rows.append({
                "account": child_name,
                "indent": 2,
                "is_group": 0,
                "monthly_credit": monthly_receipt,
                "annually_credit": annual_receipt,
                "monthly_debit": 0.0,
                "anually_debit": 0.0,
            })

        opening_balance_rows.append({
            "account": parent_name,
            "indent": 1,
            "is_group": 1,
            "monthly_credit": parent_monthly_receipt,
            "annually_credit": parent_annual_receipt,
            "monthly_debit": 0.0,
            "anually_debit": 0.0,
        })

        opening_balance_rows.extend(child_rows)
   
    closing_balance_rows = [{
        "account": _("11 - Closing Balance"),
        "indent": 0,
        "is_group": 1,
        "monthly_credit": 0.0,
        "annually_credit": 0.0,
        "monthly_debit": 0.0,
        "anually_debit": 0.0,
    }]

    closing_groups = [
        {
            "label": "Cash",
            "source_parent": "12 a - Cash - RBA",
            "children": ["80.01 - Cash Transactions - RBA"],
        },
        {
            "label": "Bank",
            "source_parent": "12 b - Bank - RBA",
            "children": ["80.02 - Bank Transactions - RBA"],
        },
    ]

    total_closing_monthly_debit = 0.0
    total_closing_annual_debit = 0.0

    for group in closing_groups:
        child_closing_rows = []

        group_monthly_debit = 0.0
        group_annual_debit = 0.0

        for child_name in group["children"]:
            if not frappe.db.exists(
                "Account",
                {
                    "name": child_name,
                    "company": filters.company,
                },
            ):
                continue

            account_totals = totals.get(child_name, {})

            monthly_debit = flt(
                account_totals.get("monthly_debit", 0.0)
            )

            annual_debit = flt(
                account_totals.get("anually_debit", 0.0)
            )

            group_monthly_debit += monthly_debit
            group_annual_debit += annual_debit

            child_closing_rows.append({
                "account": child_name,
                "indent": 2,
                "is_group": 0,
                "monthly_credit": 0.0,
                "annually_credit": 0.0,
                "monthly_debit": monthly_debit,
                "anually_debit": annual_debit,
            })

        if not child_closing_rows:
            continue

        total_closing_monthly_debit += group_monthly_debit
        total_closing_annual_debit += group_annual_debit

        closing_balance_rows.append({
            "account": group["label"],
            "indent": 1,
            "is_group": 1,
            "monthly_credit": 0.0,
            "annually_credit": 0.0,
            "monthly_debit": group_monthly_debit,
            "anually_debit": group_annual_debit,
        })

        closing_balance_rows.extend(child_closing_rows)

    return opening_balance_rows + data + closing_balance_rows
