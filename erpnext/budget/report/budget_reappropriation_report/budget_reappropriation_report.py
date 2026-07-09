# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils import getdate, formatdate


def execute(filters=None):
    filters = frappe._dict(filters or {})

    validate_filters(filters)

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def validate_filters(filters):
    if not filters.get("fiscal_year"):
        frappe.throw(_("Fiscal Year is required"))

    fiscal_year = frappe.db.get_value(
        "Fiscal Year",
        filters.fiscal_year,
        ["year_start_date", "year_end_date"],
        as_dict=True
    )

    if not fiscal_year:
        frappe.throw(_("Fiscal Year {0} does not exist").format(filters.fiscal_year))

    filters.year_start_date = getdate(fiscal_year.year_start_date)
    filters.year_end_date = getdate(fiscal_year.year_end_date)

    if not filters.get("from_date"):
        filters.from_date = filters.year_start_date

    if not filters.get("to_date"):
        filters.to_date = filters.year_end_date

    filters.from_date = getdate(filters.from_date)
    filters.to_date = getdate(filters.to_date)

    if filters.from_date > filters.to_date:
        frappe.throw(_("From Date cannot be greater than To Date"))

    if filters.from_date < filters.year_start_date or filters.from_date > filters.year_end_date:
        frappe.msgprint(
            _("From Date should be within the Fiscal Year. Assuming From Date = {0}")
            .format(formatdate(filters.year_start_date))
        )
        filters.from_date = filters.year_start_date

    if filters.to_date < filters.year_start_date or filters.to_date > filters.year_end_date:
        frappe.msgprint(
            _("To Date should be within the Fiscal Year. Assuming To Date = {0}")
            .format(formatdate(filters.year_end_date))
        )
        filters.to_date = filters.year_end_date


def get_data(filters):
    conditions = [
        "br.docstatus = 1",
        "br.appropriation_on BETWEEN %(from_date)s AND %(to_date)s"
    ]

    values = {
        "from_date": filters.from_date,
        "to_date": filters.to_date
    }

    if filters.get("company"):
        conditions.append("br.company = %(company)s")
        values["company"] = filters.company

    if filters.get("budget_against"):
        conditions.append("br.budget_against = %(budget_against)s")
        values["budget_against"] = filters.budget_against

    if filters.get("from_cc"):
        conditions.append("br.from_cost_center = %(from_cc)s")
        values["from_cc"] = filters.from_cc

    if filters.get("to_cc"):
        conditions.append("br.to_cost_center = %(to_cc)s")
        values["to_cc"] = filters.to_cc

    if filters.get("from_acc"):
        conditions.append("brd.from_account = %(from_acc)s")
        values["from_acc"] = filters.from_acc

    if filters.get("to_acc"):
        conditions.append("brd.to_account = %(to_acc)s")
        values["to_acc"] = filters.to_acc

    query = """
        SELECT
            br.name AS voucher_no,
            br.appropriation_on AS date,
            br.company AS company,
            br.fiscal_year AS fiscal_year,
            br.budget_against AS budget_against,

            br.from_cost_center AS from_cc,
            br.to_cost_center AS to_cc,

            brd.from_account AS from_acc,
            brd.to_account AS to_acc,

            brd.from_budget_activity AS from_budget_activity,
            brd.to_budget_activity AS to_budget_activity,

            brd.from_budget_sub_activity AS from_budget_sub_activity,
            brd.to_budget_sub_activity AS to_budget_sub_activity,

            from_sof.fic AS source_of_fund,
            to_sof.fic AS to_source_of_fund,

            brd.amount AS from_approved_budget,
            brd.amount AS to_approved_budget,

            br.total_reappropiation_amount AS amount,

            br.remark AS remarks

        FROM `tabBudget Reappropiation` br

        INNER JOIN `tabBudget Reappropiation Detail` brd
            ON brd.parent = br.name

        LEFT JOIN `tabSource of Fund` from_sof
            ON from_sof.name = brd.source_of_fund

        LEFT JOIN `tabSource of Fund` to_sof
            ON to_sof.name = brd.to_source_of_fund

        WHERE {conditions}

        ORDER BY
            br.appropriation_on ASC,
            br.name ASC,
            brd.idx ASC
    """.format(conditions=" AND ".join(conditions))

    return frappe.db.sql(query, values, as_dict=True)


def get_columns():
    return [
        {
            "fieldname": "date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 110
        },
        {
            "fieldname": "voucher_no",
            "label": _("Voucher No"),
            "fieldtype": "Link",
            "options": "Budget Reappropiation",
            "width": 150
        },
        {
            "fieldname": "from_cc",
            "label": _("From Cost Center"),
            "fieldtype": "Link",
            "options": "Cost Center",
            "width": 220
        },
        {
            "fieldname": "to_cc",
            "label": _("To Cost Center"),
            "fieldtype": "Link",
            "options": "Cost Center",
            "width": 220
        },
        {
            "fieldname": "from_acc",
            "label": _("From Account"),
            "fieldtype": "Link",
            "options": "Account",
            "width": 220
        },
        {
            "fieldname": "to_acc",
            "label": _("To Account"),
            "fieldtype": "Link",
            "options": "Account",
            "width": 220
        },
        {
            "fieldname": "from_budget_activity",
            "label": _("From Budget Activity"),
            "fieldtype": "Link",
            "options": "Budget Activity",
            "width": 220
        },
        {
            "fieldname": "to_budget_activity",
            "label": _("To Budget Activity"),
            "fieldtype": "Link",
            "options": "Budget Activity",
            "width": 220
        },
        {
            "fieldname": "from_budget_sub_activity",
            "label": _("From Budget Sub Activity"),
            "fieldtype": "Link",
            "options": "Budget Sub Activity",
            "width": 220
        },
        {
            "fieldname": "to_budget_sub_activity",
            "label": _("To Budget Sub Activity"),
            "fieldtype": "Link",
            "options": "Budget Sub Activity",
            "width": 220
        },
        {
            "fieldname": "source_of_fund",
            "label": _("From Financial Code"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "to_source_of_fund",
            "label": _("To Financial Code"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "from_approved_budget",
            "label": _("From Approved Budget"),
            "fieldtype": "Currency",
            "width": 160
        },
        {
            "fieldname": "to_approved_budget",
            "label": _("To Approved Budget"),
            "fieldtype": "Currency",
            "width": 160
        },
        {
            "fieldname": "amount",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "fieldname": "remarks",
            "label": _("Remarks"),
            "fieldtype": "Data",
            "width": 250
        }
    ]