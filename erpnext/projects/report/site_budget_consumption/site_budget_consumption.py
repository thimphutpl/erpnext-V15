# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data



import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate


SITE_WAREHOUSE_ACCOUNTS = {
    "Gyalpozhing - GYALSUNG": "A202021003 - Gyalpozhing Warehouse - GYALSUNG",
    "Jamtsholing - GYALSUNG": "A202021006 - Jamtsholing Warehouse - GYALSUNG",
    "Khotokha - GYALSUNG": "A202021002 - Khotokha Warehouse - GYALSUNG",
    "Pemathang - GYALSUNG": "A202021004 - Pemathang Warehouse - GYALSUNG",
    "Tareythang - GYALSUNG": "A202021005 - Tareythang Warehouse - GYALSUNG",
}
HEAD_OFFICE_COST_CENTER = "Head Office - GYALSUNG"
PARENT_WAREHOUSE_ACCOUNTS = {
    **SITE_WAREHOUSE_ACCOUNTS,
    HEAD_OFFICE_COST_CENTER: "A202021001 - Head Office Warehouse - GYALSUNG",
}
DEFAULT_ADVANCE_ACCOUNT = "A202022004 - Advance to Supplier - GYALSUNG"
OPERATING_EXPENSE_ACCOUNT = "Operating Expenses - GYALSUNG"


def execute(filters=None):
    filters = frappe._dict(filters or {})
    filters.company = filters.get("company") or "GYALSUNG INFRA"
    filters.from_date = filters.get("from_date") or "2020-01-01"
    filters.to_date = filters.get("to_date") or nowdate()

    validate_filters(filters)

    columns = get_columns()
    data = get_data(filters)

    return columns, data, None


def validate_filters(filters):
    required = {
        "company": _("Company"),
    }

    for fieldname, label in required.items():
        if not filters.get(fieldname):
            frappe.throw(_("{0} is required").format(label))

    if getdate(filters.from_date) > getdate(filters.to_date):
        frappe.throw(_("From Date cannot be after To Date"))


def get_columns():
    return [
        {
            "label": _("Site / Parent Cost Center"),
            "fieldname": "cost_center",
            "fieldtype": "Link",
            "options": "Cost Center",
            "width": 240,
        },
        {
            "label": _("Estimated Budget"),
            "fieldname": "estimated_budget",
            "fieldtype": "Currency",
            "width": 160,
        },
        {
            "label": _("Actual Expenses"),
            "fieldname": "actual_annual_budget",
            "fieldtype": "Currency",
            "width": 180,
        },
        {
            "label": _("Inventory Balance"),
            "fieldname": "inventory_budget",
            "fieldtype": "Currency",
            "width": 170,
        },
        {
            "label": _("Advance to Suppliers Balance"),
            "fieldname": "advance_to_suppliers",
            "fieldtype": "Currency",
            "width": 190,
        },
        {
            "label": _("Total Expenses"),
            "fieldname": "budget_consumed",
            "fieldtype": "Currency",
            "width": 200,
        },
    ]


def get_data(filters):
    site_filters = {
        "company": filters.company,
        "is_group": 1,
        "name": ["in", list(PARENT_WAREHOUSE_ACCOUNTS)],
    }
    sites = frappe.get_all(
        "Cost Center",
        filters=site_filters,
        fields=["name", "lft", "rgt", "estimated_budget"],
        order_by="name asc",
    )
    if not sites:
        return []

    amounts = get_site_amounts(filters, sites)
    data = []

    for site in sites:
        actual_annual_budget, inventory_budget, advance_to_suppliers = amounts[site.name]

        budget_consumed = (
            actual_annual_budget
            + inventory_budget
            + advance_to_suppliers
        )

        data.append({
            "cost_center": site.name,
            "estimated_budget": flt(site.estimated_budget),
            "actual_annual_budget": actual_annual_budget,
            "inventory_budget": inventory_budget,
            "advance_to_suppliers": advance_to_suppliers,
            "budget_consumed": budget_consumed,
        })

    return data


def get_site_amounts(filters, sites):
    """Roll up closing balances, including opening P&L and default book entries."""
    cost_centers = frappe.get_all(
        "Cost Center", filters={"company": filters.company}, fields=["name", "lft", "rgt"]
    )
    cost_centers_by_name = {cc.name: cc for cc in cost_centers}
    site_by_cost_center = {
        cc.name: site.name
        for site in sites
        for cc in cost_centers
        if cc.lft >= site.lft and cc.rgt <= site.rgt
    }
    accounts = frappe.get_all(
        "Account", filters={"company": filters.company},
        fields=["name", "lft", "rgt", "root_type"],
    )
    accounts_by_name = {account.name: account for account in accounts}

    def descendants(account_name):
        parent = accounts_by_name.get(account_name)
        if not parent:
            frappe.throw(_("Account {0} not found for company {1}").format(account_name, filters.company))
        return {
            account.name for account in accounts
            if account.lft >= parent.lft and account.rgt <= parent.rgt
        }

    # Actual Budget Used is the Operating Expenses row in Trial Balance,
    # including this parent account and every account below it.
    expense_accounts = descendants(OPERATING_EXPENSE_ACCOUNT)
    warehouse_accounts = {
        site.name: descendants(PARENT_WAREHOUSE_ACCOUNTS[site.name])
        for site in sites
    }
    site_by_warehouse_account = {
        account: site_name
        for site_name, names in warehouse_accounts.items()
        for account in names
    }
    advance_accounts = descendants(DEFAULT_ADVANCE_ACCOUNT)
    relevant_accounts = expense_accounts | advance_accounts
    for names in warehouse_accounts.values():
        relevant_accounts |= names

    # Match Trial Balance with Include Default FB Entries enabled and no
    # specific finance book selected: blank entries plus the company's default.
    default_finance_book = frappe.db.get_value("Company", filters.company, "default_finance_book")
    finance_books = tuple(sorted({"", default_finance_book or ""}))

    # The covering ledger index supplies balances without fetching every ledger row.
    # If a specific cost center filter is provided, limit the cost centers
    # to that cost center and its descendants so the Trial Balance matches
    # the user's filtered view.
    if filters.get("cost_center"):
        selected = filters.get("cost_center")
        parent = cost_centers_by_name.get(selected)
        if not parent:
            frappe.throw(_("Cost Center {0} not found for company {1}").format(selected, filters.company))
        cost_center_names = tuple(
            cc.name for cc in cost_centers if cc.lft >= parent.lft and cc.rgt <= parent.rgt
        )
    else:
        cost_center_names = tuple(site_by_cost_center)

    # MariaDB can underestimate random row lookups through the account-only index.
    # Use the covering index when installed, retaining the scan until migration.
    ledger_index = (
        "site_budget_consumption_index"
        if frappe.db.has_index("tabGL Entry", "site_budget_consumption_index")
        else "PRIMARY"
    )
    ledger_totals = frappe.db.sql(
        f"""
        SELECT
            cost_center, account,
            SUM(debit - credit) AS closing_balance
        FROM `tabGL Entry` FORCE INDEX ({ledger_index})
        WHERE company = %(company)s
            AND is_cancelled = 0
            AND posting_date <= %(to_date)s
            AND (finance_book IN %(finance_books)s OR finance_book IS NULL)
            AND (cost_center IN %(cost_centers)s OR account IN %(warehouse_accounts)s)
            AND account IN %(accounts)s
        GROUP BY cost_center, account
        """,
        {
            "company": filters.company,
            "to_date": filters.to_date,
            "finance_books": finance_books,
            "cost_centers": cost_center_names,
            "warehouse_accounts": tuple(sorted(site_by_warehouse_account)),
            "accounts": tuple(sorted(relevant_accounts)),
        },
        as_dict=True,
    )
    amounts = {site.name: [0.0, 0.0, 0.0] for site in sites}
    for row in ledger_totals:
        # Inventory matches the site's warehouse row in Trial Balance with no
        # cost center selected, including entries assigned elsewhere or nowhere.
        warehouse_site = site_by_warehouse_account.get(row.account)
        if warehouse_site:
            amounts[warehouse_site][1] += flt(row.closing_balance)

        site_name = site_by_cost_center.get(row.cost_center)
        if not site_name:
            continue
        if row.account in expense_accounts:
            # Trial Balance closing P&L = opening balance + period movement.
            amounts[site_name][0] += frappe.utils.flt(row.closing_balance)
        if row.account in advance_accounts:
            amounts[site_name][2] += frappe.utils.flt(row.closing_balance)
    return amounts
