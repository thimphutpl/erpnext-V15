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
            "label": _("Sub Program"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "ac",
            "label": _("Budget Activity"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "fic",
            "label": _("Source of Fund"),
            "fieldtype": "Data",
            "width": 150
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
            "width": 150
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
    final_data = combine_data(
        monthly_data,
        annual_data
    )

    # Add summary rows
    final_data = add_summary_rows(
        final_data,
        monthly_data,
        annual_data,
        filters
    )

    return final_data


def get_monthly_data(filters):
    conditions = []
    values = {}

    if filters.get("company"):
        conditions.append(
            "gle.company = %(company)s"
        )
        values["company"] = filters.get("company")

    if filters.get("fiscal_year"):
        conditions.append(
            "gle.fiscal_year = %(fiscal_year)s"
        )
        values["fiscal_year"] = filters.get("fiscal_year")

    if filters.get("from_date") and filters.get("to_date"):
        conditions.append(
            "gle.posting_date BETWEEN %(from_date)s AND %(to_date)s"
        )
        values["from_date"] = filters.get("from_date")
        values["to_date"] = filters.get("to_date")

    if filters.get("cost_center"):
        conditions.append(
            "gle.cost_center = %(cost_center)s"
        )
        values["cost_center"] = filters.get("cost_center")

    # Only include GL entries with budget_activity
    conditions.append(
        "gle.budget_activity IS NOT NULL"
    )

    conditions.append(
        "gle.budget_activity != ''"
    )

    conditions.append(
        "gle.is_cancelled = 0"
    )

    where_clause = " AND ".join(conditions)

    sql_query = """
        SELECT
            cc.cost_center_number AS sp,
            cc.cost_center_name AS cost_center_name,

            ba.activity_code AS ac,
            ba.activity_name AS ac_name,

            sof.fic AS fic,
            sof.source_of_fund AS fic_name,

            acc.account_number AS obc,
            acc.name AS account_name,
            acc.parent_account,

            -- Monthly Current
            SUM(
                IF(
                    acc.parent_account LIKE
                        '%%10 a - Current - RBA%%'
                    OR acc.parent_account =
                        '10 a - Current - RBA',

                    gle.debit - gle.credit,
                    0
                )
            ) AS monthly_current,

            -- Monthly Capital
            SUM(
                IF(
                    acc.parent_account LIKE
                        '%%10 b - Capital - RBA%%'
                    OR acc.parent_account =
                        '10 b - Capital - RBA',

                    gle.debit - gle.credit,
                    0
                )
            ) AS monthly_capital,

            -- Monthly Lending
            SUM(
                IF(
                    acc.parent_account LIKE
                        '%%10 c - Lending - RBA%%'
                    OR acc.parent_account =
                        '10 c - Lending - RBA',

                    gle.debit - gle.credit,
                    0
                )
            ) AS monthly_lending,

            -- Monthly Repayment
            SUM(
                IF(
                    acc.parent_account LIKE
                        '%%10 d - Repayment - RBG%%'
                    OR acc.parent_account =
                        '10 d - Repayment - RBG',

                    gle.debit - gle.credit,
                    0
                )
            ) AS monthly_repayment,

            -- Monthly Personal Advance
            SUM(
                IF(
                    acc.account_number = '88.01',
                    gle.debit - gle.credit,
                    0
                )
            ) AS monthly_personal_advance,

            -- Monthly Suspense
            SUM(
                IF(
                    acc.account_number IN (
                        '88.02',
                        '89.01',
                        '89.02'
                    ),

                    gle.debit - gle.credit,
                    0
                )
            ) AS monthly_suspense

        FROM
            `tabGL Entry` gle

        LEFT JOIN
            `tabCost Center` cc
            ON gle.cost_center = cc.name

        LEFT JOIN
            `tabBudget Activity` ba
            ON gle.budget_activity = ba.name

        LEFT JOIN
            `tabSource of Fund` sof
            ON gle.source_of_fund = sof.name

        LEFT JOIN
            `tabAccount` acc
            ON gle.account = acc.name

        WHERE
            {where_clause}

        GROUP BY
            cc.cost_center_number,
            cc.cost_center_name,

            ba.activity_code,
            ba.activity_name,

            sof.fic,
            sof.source_of_fund,

            acc.account_number,
            acc.name,
            acc.parent_account

    """.format(
        where_clause=where_clause
    )

    return frappe.db.sql(
        sql_query,
        values,
        as_dict=1
    )


def get_annual_data(filters):
    # Get annual progressive data from Fiscal Year start
    # to the selected To Date.

    fiscal_year = filters.get("fiscal_year")

    if not fiscal_year:
        return []

    fy_data = frappe.db.get_value(
        "Fiscal Year",
        fiscal_year,
        [
            "year_start_date",
            "year_end_date"
        ],
        as_dict=True
    )

    if not fy_data:
        return []

    annual_filters = {
        "company": filters.get("company"),
        "fiscal_year": filters.get("fiscal_year"),
        "from_date": fy_data.year_start_date,
        "to_date": filters.get(
            "to_date",
            fy_data.year_end_date
        )
    }

    if filters.get("cost_center"):
        annual_filters["cost_center"] = filters.get(
            "cost_center"
        )

    conditions = []
    values = {}

    if annual_filters.get("company"):
        conditions.append(
            "gle.company = %(company)s"
        )
        values["company"] = annual_filters.get(
            "company"
        )

    if annual_filters.get("fiscal_year"):
        conditions.append(
            "gle.fiscal_year = %(fiscal_year)s"
        )
        values["fiscal_year"] = annual_filters.get(
            "fiscal_year"
        )

    if (
        annual_filters.get("from_date")
        and annual_filters.get("to_date")
    ):
        conditions.append(
            "gle.posting_date BETWEEN %(from_date)s AND %(to_date)s"
        )

        values["from_date"] = annual_filters.get(
            "from_date"
        )

        values["to_date"] = annual_filters.get(
            "to_date"
        )

    if annual_filters.get("cost_center"):
        conditions.append(
            "gle.cost_center = %(cost_center)s"
        )

        values["cost_center"] = annual_filters.get(
            "cost_center"
        )

    conditions.append(
        "gle.budget_activity IS NOT NULL"
    )

    conditions.append(
        "gle.budget_activity != ''"
    )

    conditions.append(
        "gle.is_cancelled = 0"
    )

    where_clause = " AND ".join(conditions)

    sql_query = """
        SELECT
            cc.cost_center_number AS sp,
            cc.cost_center_name AS cost_center_name,

            ba.activity_code AS ac,
            ba.activity_name AS ac_name,

            sof.fic AS fic,
            sof.source_of_fund AS fic_name,

            acc.account_number AS obc,

            -- Annual Current
            SUM(
                IF(
                    acc.parent_account LIKE
                        '%%10 a - Current - RBA%%'
                    OR acc.parent_account =
                        '10 a - Current - RBA',

                    gle.debit - gle.credit,
                    0
                )
            ) AS annual_current,

            -- Annual Capital
            SUM(
                IF(
                    acc.parent_account LIKE
                        '%%10 b - Capital - RBA%%'
                    OR acc.parent_account =
                        '10 b - Capital - RBA',

                    gle.debit - gle.credit,
                    0
                )
            ) AS annual_capital,

            -- Annual Lending
            SUM(
                IF(
                    acc.parent_account LIKE
                        '%%10 c - Lending - RBA%%'
                    OR acc.parent_account =
                        '10 c - Lending - RBA',

                    gle.debit - gle.credit,
                    0
                )
            ) AS annual_lending,

            -- Annual Repayment
            SUM(
                IF(
                    acc.parent_account LIKE
                        '%%10 d - Repayment - RBG%%'
                    OR acc.parent_account =
                        '10 d - Repayment - RBG',

                    gle.debit - gle.credit,
                    0
                )
            ) AS annual_repayment,

            -- Annual Personal Advance
            SUM(
                IF(
                    acc.account_number = '88.01',
                    gle.debit - gle.credit,
                    0
                )
            ) AS annual_personal_advance,

            -- Annual Suspense
            SUM(
                IF(
                    acc.account_number IN (
                        '88.02',
                        '89.01',
                        '89.02'
                    ),

                    gle.debit - gle.credit,
                    0
                )
            ) AS annual_suspense

        FROM
            `tabGL Entry` gle

        LEFT JOIN
            `tabCost Center` cc
            ON gle.cost_center = cc.name

        LEFT JOIN
            `tabBudget Activity` ba
            ON gle.budget_activity = ba.name

        LEFT JOIN
            `tabSource of Fund` sof
            ON gle.source_of_fund = sof.name

        LEFT JOIN
            `tabAccount` acc
            ON gle.account = acc.name

        WHERE
            {where_clause}

        GROUP BY
            cc.cost_center_number,
            cc.cost_center_name,

            ba.activity_code,
            ba.activity_name,

            sof.fic,
            sof.source_of_fund,

            acc.account_number

    """.format(
        where_clause=where_clause
    )

    return frappe.db.sql(
        sql_query,
        values,
        as_dict=1
    )


def combine_code_and_name(code, name):
    code = str(code or "").strip()
    name = str(name or "").strip()

    if code and name:
        return "{0} - {1}".format(
            code,
            name
        )

    return code or name


def combine_data(monthly_data, annual_data):
    final_data = []
    annual_dict = {}

    # Annual data key uses the original raw SP code
    for row in annual_data:
        key = (
            row.get("sp"),
            row.get("ac"),
            row.get("fic"),
            row.get("obc")
        )

        annual_dict[key] = row

    # Combine monthly and annual data
    for monthly_row in monthly_data:
        # Match using the original raw SP code
        key = (
            monthly_row.get("sp"),
            monthly_row.get("ac"),
            monthly_row.get("fic"),
            monthly_row.get("obc")
        )

        annual_row = annual_dict.get(
            key,
            {}
        )

        monthly_amount = (
            flt(
                monthly_row.get(
                    "monthly_current",
                    0
                )
            )
            + flt(
                monthly_row.get(
                    "monthly_capital",
                    0
                )
            )
            + flt(
                monthly_row.get(
                    "monthly_lending",
                    0
                )
            )
            + flt(
                monthly_row.get(
                    "monthly_repayment",
                    0
                )
            )
        )

        annual_amount = (
            flt(
                annual_row.get(
                    "annual_current",
                    0
                )
            )
            + flt(
                annual_row.get(
                    "annual_capital",
                    0
                )
            )
            + flt(
                annual_row.get(
                    "annual_lending",
                    0
                )
            )
            + flt(
                annual_row.get(
                    "annual_repayment",
                    0
                )
            )
        )

        final_row = {
            # Show SP code and Cost Center name together
            "sp": combine_code_and_name(
                monthly_row.get(
                    "sp",
                    ""
                ),
                monthly_row.get(
                    "cost_center_name",
                    ""
                )
            ),

            # Keep Cost Center name available in returned data
            # but do not show it as a separate column
            "cost_center_name": monthly_row.get(
                "cost_center_name",
                ""
            ),

            "ac": monthly_row.get(
                "ac",
                ""
            ),

            "ac_name": monthly_row.get(
                "ac_name",
                ""
            ),

            "fic": monthly_row.get(
                "fic",
                ""
            ),

            "fic_name": monthly_row.get(
                "fic_name",
                ""
            ),

            "obc": monthly_row.get(
                "obc",
                ""
            ),

            "names": monthly_row.get(
                "account_name",
                ""
            ),

            "monthly_current": flt(
                monthly_row.get(
                    "monthly_current",
                    0
                )
            ),

            "monthly_capital": flt(
                monthly_row.get(
                    "monthly_capital",
                    0
                )
            ),

            "monthly_lending": flt(
                monthly_row.get(
                    "monthly_lending",
                    0
                )
            ),

            "monthly_repayment": flt(
                monthly_row.get(
                    "monthly_repayment",
                    0
                )
            ),

            "monthly_amount": monthly_amount,

            "monthly_personal_advance": flt(
                monthly_row.get(
                    "monthly_personal_advance",
                    0
                )
            ),

            "monthly_suspense": flt(
                monthly_row.get(
                    "monthly_suspense",
                    0
                )
            ),

            "annual_current": flt(
                annual_row.get(
                    "annual_current",
                    0
                )
            ),

            "annual_capital": flt(
                annual_row.get(
                    "annual_capital",
                    0
                )
            ),

            "annual_lending": flt(
                annual_row.get(
                    "annual_lending",
                    0
                )
            ),

            "annual_repayment": flt(
                annual_row.get(
                    "annual_repayment",
                    0
                )
            ),

            "annual_amount": annual_amount,

            "annual_personal_advance": flt(
                annual_row.get(
                    "annual_personal_advance",
                    0
                )
            ),

            "annual_suspense": flt(
                annual_row.get(
                    "annual_suspense",
                    0
                )
            )
        }

        # Only include rows having amounts
        if (
            final_row["monthly_amount"] != 0
            or final_row["annual_amount"] != 0
            or final_row["monthly_personal_advance"] != 0
            or final_row["annual_personal_advance"] != 0
        ):
            final_data.append(
                final_row
            )

    # Sort report data
    final_data.sort(
        key=lambda row: (
            row.get("sp") or "",
            row.get("ac") or "",
            row.get("fic") or "",
            row.get("obc") or ""
        )
    )

    return final_data


def add_summary_rows(
    final_data,
    monthly_data,
    annual_data,
    filters
):
    if not final_data:
        return final_data

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

    # Monthly totals
    for row in monthly_data:
        monthly_totals["current"] += flt(
            row.get(
                "monthly_current",
                0
            )
        )

        monthly_totals["capital"] += flt(
            row.get(
                "monthly_capital",
                0
            )
        )

        monthly_totals["lending"] += flt(
            row.get(
                "monthly_lending",
                0
            )
        )

        monthly_totals["repayment"] += flt(
            row.get(
                "monthly_repayment",
                0
            )
        )

        monthly_totals["personal_advance"] += flt(
            row.get(
                "monthly_personal_advance",
                0
            )
        )

        monthly_totals["suspense"] += flt(
            row.get(
                "monthly_suspense",
                0
            )
        )

    # Annual totals
    for row in annual_data:
        annual_totals["current"] += flt(
            row.get(
                "annual_current",
                0
            )
        )

        annual_totals["capital"] += flt(
            row.get(
                "annual_capital",
                0
            )
        )

        annual_totals["lending"] += flt(
            row.get(
                "annual_lending",
                0
            )
        )

        annual_totals["repayment"] += flt(
            row.get(
                "annual_repayment",
                0
            )
        )

        annual_totals["personal_advance"] += flt(
            row.get(
                "annual_personal_advance",
                0
            )
        )

        annual_totals["suspense"] += flt(
            row.get(
                "annual_suspense",
                0
            )
        )

    def add_breakdown_rows(section_name):
        rows = []

        # Section heading
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

        # Current total
        rows.append({
            "sp": "",
            "ac": "",
            "fic": "",
            "obc": "",
            "names": "Current (Total)",

            "monthly_current":
                monthly_totals["current"],

            "monthly_capital": 0,
            "monthly_lending": 0,
            "monthly_repayment": 0,

            "monthly_amount":
                monthly_totals["current"],

            "monthly_personal_advance":
                monthly_totals["personal_advance"],

            "monthly_suspense":
                monthly_totals["suspense"],

            "annual_current":
                annual_totals["current"],

            "annual_capital": 0,
            "annual_lending": 0,
            "annual_repayment": 0,

            "annual_amount":
                annual_totals["current"],

            "annual_personal_advance":
                annual_totals["personal_advance"],

            "annual_suspense":
                annual_totals["suspense"],

            "is_summary": 1,
            "indent": 1,
            "is_breakdown": 1
        })

        # Capital total
        rows.append({
            "sp": "",
            "ac": "",
            "fic": "",
            "obc": "",
            "names": "Capital (Total)",

            "monthly_current": 0,

            "monthly_capital":
                monthly_totals["capital"],

            "monthly_lending": 0,
            "monthly_repayment": 0,

            "monthly_amount":
                monthly_totals["capital"],

            "monthly_personal_advance": 0,
            "monthly_suspense": 0,

            "annual_current": 0,

            "annual_capital":
                annual_totals["capital"],

            "annual_lending": 0,
            "annual_repayment": 0,

            "annual_amount":
                annual_totals["capital"],

            "annual_personal_advance": 0,
            "annual_suspense": 0,

            "is_summary": 1,
            "indent": 1,
            "is_breakdown": 1
        })

        # Lending total
        rows.append({
            "sp": "",
            "ac": "",
            "fic": "",
            "obc": "",
            "names": "Lending (Total)",

            "monthly_current": 0,
            "monthly_capital": 0,

            "monthly_lending":
                monthly_totals["lending"],

            "monthly_repayment": 0,

            "monthly_amount":
                monthly_totals["lending"],

            "monthly_personal_advance": 0,
            "monthly_suspense": 0,

            "annual_current": 0,
            "annual_capital": 0,

            "annual_lending":
                annual_totals["lending"],

            "annual_repayment": 0,

            "annual_amount":
                annual_totals["lending"],

            "annual_personal_advance": 0,
            "annual_suspense": 0,

            "is_summary": 1,
            "indent": 1,
            "is_breakdown": 1
        })

        # Repayment total
        rows.append({
            "sp": "",
            "ac": "",
            "fic": "",
            "obc": "",
            "names": "Repayment (Total)",

            "monthly_current": 0,
            "monthly_capital": 0,
            "monthly_lending": 0,

            "monthly_repayment":
                monthly_totals["repayment"],

            "monthly_amount":
                monthly_totals["repayment"],

            "monthly_personal_advance": 0,
            "monthly_suspense": 0,

            "annual_current": 0,
            "annual_capital": 0,
            "annual_lending": 0,

            "annual_repayment":
                annual_totals["repayment"],

            "annual_amount":
                annual_totals["repayment"],

            "annual_personal_advance": 0,
            "annual_suspense": 0,

            "is_summary": 1,
            "indent": 1,
            "is_breakdown": 1
        })

        return rows

    blank_row = {
        "sp": "",
        "ac": "",
        "fic": "",
        "obc": "",
        "names": "",
        "monthly_amount": 0,
        "annual_amount": 0,
        "is_summary": 1,
        "indent": 0
    }

    # Blank row before Total OBC/GL
    final_data.append(
        dict(blank_row)
    )

    # Total OBC/GL
    final_data.extend(
        add_breakdown_rows(
            "Total OBC/GL"
        )
    )

    # Blank row before Total Activity
    final_data.append(
        dict(blank_row)
    )

    # Total Activity
    final_data.extend(
        add_breakdown_rows(
            "Total Activity"
        )
    )

    # Blank row before Total Sub-program
    final_data.append(
        dict(blank_row)
    )

    # Total Sub-program
    final_data.extend(
        add_breakdown_rows(
            "Total Sub-program"
        )
    )

    # Blank row before Total Program
    final_data.append(
        dict(blank_row)
    )

    # Total Program
    final_data.extend(
        add_breakdown_rows(
            "Total Program"
        )
    )

    return final_data