from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP

import frappe
from frappe import _
from frappe.desk.query_report import get_report_doc
from frappe.utils import now_datetime, nowdate

from erpnext.projects.report.site_budget_consumption.site_budget_consumption import (
    HEAD_OFFICE_COST_CENTER,
    SITE_WAREHOUSE_ACCOUNTS,
    execute,
)


@frappe.whitelist()
def get_site_budget_chart():
    """Use the report's permissions and live calculations for the dashboard."""
    get_report_doc("Site Budget Consumption")
    company = "GYALSUNG INFRA"
    if not frappe.get_list("Company", filters={"name": company}, pluck="name", limit_page_length=1):
        frappe.throw(_("You do not have permission to view this company's budget."), frappe.PermissionError)

    filters = {"company": company, "from_date": "2020-01-01", "to_date": nowdate()}
    _columns, rows, _message = execute(filters)
    sites = [
        {
            "cost_center": row["cost_center"],
            "site": row["cost_center"].removesuffix(" - GYALSUNG"),
            "estimated_budget": row["estimated_budget"],
            "actual_expenses": row["actual_annual_budget"],
            "inventory_balance": row["inventory_budget"],
            "advance_to_suppliers_balance": row["advance_to_suppliers"],
            "total_expenses": row["budget_consumed"],
        }
        for row in rows
        if row["cost_center"] in SITE_WAREHOUSE_ACCOUNTS
    ]
    head_office_total = next(
        (row["budget_consumed"] for row in rows if row["cost_center"] == HEAD_OFFICE_COST_CENTER),
        None,
    )
    allocation_message = allocate_head_office_expenses(sites, head_office_total)
    return {
        **filters,
        "currency": frappe.db.get_value("Company", company, "default_currency"),
        "updated_at": str(now_datetime()),
        "sites": sites,
        "head_office_total_expenses": head_office_total,
        "allocation_message": allocation_message,
        "totals": {
            field: sum(site[field] or 0 for site in sites)
            for field in (
                "estimated_budget", "actual_expenses", "inventory_balance",
                "advance_to_suppliers_balance", "head_office_allocation", "total_expenses",
            )
        },
    }


def allocate_head_office_expenses(sites, head_office_total):
    """Allocate HQ costs by the five sites' budgets, reconciling to the cent."""
    for site in sites:
        site["head_office_allocation"] = None
        site["head_office_allocation_percent"] = None

    if head_office_total is None:
        return _("Head Office allocation is unavailable because the Head Office Cost Center was not found.")

    budgets = [Decimal(str(site["estimated_budget"] or 0)) for site in sites]
    total_budget = sum(budgets)
    if total_budget <= 0 or any(budget < 0 for budget in budgets):
        return _("Head Office allocation requires non-negative site budgets and a combined estimated budget greater than zero.")

    # Distribute whole cents by largest remainder so displayed allocations add
    # up to HQ's total, without rounding the budget percentages first.
    total_cents = (Decimal(str(head_office_total)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    exact_cents = [total_cents * budget / total_budget for budget in budgets]
    allocated_cents = [amount.to_integral_value(rounding=ROUND_FLOOR) for amount in exact_cents]
    remainder = int(total_cents - sum(allocated_cents))
    order = sorted(range(len(sites)), key=lambda i: exact_cents[i] - allocated_cents[i], reverse=True)
    for index in order[:remainder]:
        allocated_cents[index] += 1

    for index, site in enumerate(sites):
        site["head_office_allocation_percent"] = float(budgets[index] / total_budget * 100)
        site["head_office_allocation"] = float(allocated_cents[index] / 100)
        site["total_expenses"] = float(
            (Decimal(str(site["total_expenses"])) + allocated_cents[index] / 100)
            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )

    if any(budget == 0 for budget in budgets):
        return _("Sites with a zero or missing estimated budget receive no Head Office allocation. Enter their budgets to include them.")
