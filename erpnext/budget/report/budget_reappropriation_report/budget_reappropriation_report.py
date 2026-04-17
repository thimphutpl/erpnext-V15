# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr

def execute(filters=None):
    validate_filters(filters)
    data = get_data(filters)
    columns = get_columns()
    return columns, data

def validate_filters(filters):
    if not filters.fiscal_year:
        frappe.throw(_("Fiscal Year {0} is required").format(filters.fiscal_year))

    fiscal_year = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"], as_dict=True)
    if not fiscal_year:
        frappe.throw(_("Fiscal Year {0} does not exist").format(filters.fiscal_year))
    else:
        filters.year_start_date = getdate(fiscal_year.year_start_date)
        filters.year_end_date = getdate(fiscal_year.year_end_date)

    if not filters.from_date:
        filters.from_date = filters.year_start_date

    if not filters.to_date:
        filters.to_date = filters.year_end_date

    filters.from_date = getdate(filters.from_date)
    filters.to_date = getdate(filters.to_date)

    if filters.from_date > filters.to_date:
        frappe.throw(_("From Date cannot be greater than To Date"))

    if (filters.from_date < filters.year_start_date) or (filters.from_date > filters.year_end_date):
        frappe.msgprint(_("From Date should be within the Fiscal Year. Assuming From Date = {0}")\
            .format(formatdate(filters.year_start_date)))
        filters.from_date = filters.year_start_date

    if (filters.to_date < filters.year_start_date) or (filters.to_date > filters.year_end_date):
        frappe.msgprint(_("To Date should be within the Fiscal Year. Assuming To Date = {0}")\
            .format(formatdate(filters.year_end_date)))
        filters.to_date = filters.year_end_date

def get_data(filters):
    query = """
        select 
            t1.from_cost_center as from_cc,
            t1.to_cost_center as to_cc,
            t2.from_account as from_acc,
            t2.to_account as to_acc,
            t2.amount as amount,
            t1.remark as remarks,
            t1.appropriation_on as date,
            t2.from_budget_activity,
            t2.from_budget_sub_activity,
            t2.to_budget_activity,
            t2.to_budget_sub_activity
        from
            `tabBudget Reappropiation` as t1,
            `tabBudget Reappropiation Detail` as t2
        where t2.parent = t1.name
        and t1.docstatus = 1
        and t1.appropriation_on between %(from_date)s and %(to_date)s
    """

    query_params = {
        "from_date": filters.from_date,
        "to_date": filters.to_date
    }

    if filters.to_cc:
        query += " and t1.to_cost_center = %(to_cc)s"
        query_params["to_cc"] = filters.to_cc

    if filters.from_cc:
        query += " and t1.from_cost_center = %(from_cc)s"
        query_params["from_cc"] = filters.from_cc

    if filters.to_acc:
        query += " and t2.to_account = %(to_acc)s"
        query_params["to_acc"] = filters.to_acc

    if filters.from_acc:
        query += " and t2.from_account = %(from_acc)s"
        query_params["from_acc"] = filters.from_acc

    app_data = frappe.db.sql(query, query_params, as_dict=True)

    data = []
    if app_data:
        for a in app_data:
            row = {
                "to_cc": a.to_cc,
                "to_acc": a.to_acc,
                "from_cc": a.from_cc,
                "from_acc": a.from_acc,
                "amount": a.amount,
                "date": a.date,
                "remarks": a.remarks,
                "from_budget_activity": a.from_budget_activity,
                "from_budget_sub_activity": a.from_budget_sub_activity,
                "to_budget_activity": a.to_budget_activity,
                "to_budget_sub_activity": a.to_budget_sub_activity
            }
            data.append(row)
    
    return data

def get_columns():
    return [
        {
            "fieldname": "date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "from_cc",
            "label": _("From Cost Center"),
            "fieldtype": "Link",
            "options": "Cost Center",
            "width": 200
        },
        {
            "fieldname": "to_cc",
            "label": _("To Cost Center"),
            "fieldtype": "Link",
            "options": "Cost Center",
            "width": 200
        },
        {
            "fieldname": "from_acc",
            "label": _("From Account"),
            "fieldtype": "Link",
            "options": "Account",
            "width": 200
        },
        {
            "fieldname": "to_acc",
            "label": _("To Account"),
            "fieldtype": "Link",
            "options": "Account",
            "width": 200
        },
        {
            "fieldname": "from_budget_activity",
            "label": _("From Budget Activity"),
            "fieldtype": "Link",
            "options": "Budget Activity",
            "width": 200
        },
         {
            "fieldname": "to_budget_activity",
            "label": _("To Budget Activity"),
            "fieldtype": "Link",
            "options": "Budget Activity",
            "width": 200
        },
        {
            "fieldname": "from_budget_sub_activity",
            "label": _("From Budget Sub Activity"),
            "fieldtype": "Link",
            "options": "Budget Sub Activity",
            "width": 200
        },
        {
            "fieldname": "to_budget_sub_activity",
            "label": _("To Budget Sub Activity"),
            "fieldtype": "Link",
            "options": "Budget Sub Activity",
            "width": 200
        },
        {
            "fieldname": "amount",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 130
        }
    ]