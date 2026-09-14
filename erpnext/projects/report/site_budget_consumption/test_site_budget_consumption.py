import sqlite3
import unittest
from unittest.mock import Mock, patch

import frappe

from erpnext.projects.report.site_budget_consumption import site_budget_consumption as report


class TestSiteBudgetConsumption(unittest.TestCase):
    def setUp(self):
        self.database = sqlite3.connect(":memory:")
        self.addCleanup(self.database.close)
        self.database.row_factory = sqlite3.Row
        self.database.execute(
            """CREATE TABLE `tabGL Entry` (
                company TEXT, cost_center TEXT, account TEXT, posting_date TEXT,
                is_opening TEXT, is_cancelled INTEGER, finance_book TEXT,
                debit REAL, credit REAL
            )"""
        )
        self.site = frappe._dict(name="Gyalpozhing - GYALSUNG", lft=1, rgt=6)
        self.child = frappe._dict(name="Gyalpozhing Child", lft=2, rgt=3)
        self.warehouse = report.SITE_WAREHOUSE_ACCOUNTS[self.site.name]
        self.accounts = [
            frappe._dict(name=report.OPERATING_EXPENSE_ACCOUNT, lft=1, rgt=8, root_type="Expense"),
            frappe._dict(name="Expense", lft=2, rgt=3, root_type="Expense"),
            frappe._dict(name="Nested Operating Expense", lft=4, rgt=5, root_type="Expense"),
            frappe._dict(name=self.warehouse, lft=9, rgt=10, root_type="Asset"),
            frappe._dict(name=report.DEFAULT_ADVANCE_ACCOUNT, lft=11, rgt=12, root_type="Asset"),
            frappe._dict(name="Non-operating Expense", lft=13, rgt=14, root_type="Expense"),
        ]
        self.filters = frappe._dict(
            company="GYALSUNG INFRA", from_date="2020-01-01", to_date="2026-09-14"
        )
        database = patch.object(report.frappe, "db", Mock())
        self.mock_db = database.start()
        self.addCleanup(database.stop)
        self.mock_db.get_value.return_value = None
        self.mock_db.sql.side_effect = self.query
        get_all = patch.object(report.frappe, "get_all", side_effect=self.get_all)
        get_all.start()
        self.addCleanup(get_all.stop)

    def get_all(self, doctype, **kwargs):
        return [self.site, self.child] if doctype == "Cost Center" else self.accounts

    def query(self, sql, values, as_dict):
        # Execute the report's aggregation and predicates against a small ledger.
        sql = sql.replace(" FORCE INDEX (PRIMARY)", "")
        parameters = {}
        for key, value in values.items():
            if isinstance(value, tuple):
                names = [f"{key}_{index}" for index in range(len(value))]
                replacement = "(" + ",".join(":" + name for name in names) + ")"
                parameters.update(zip(names, value))
            else:
                replacement = ":" + key
                parameters[key] = value
            sql = sql.replace("%(" + key + ")s", replacement)
        return [frappe._dict(dict(row)) for row in self.database.execute(sql, parameters)]

    def add_entry(self, debit, credit=0, **values):
        self.database.execute(
            "INSERT INTO `tabGL Entry` VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                values.get("company", self.filters.company),
                values.get("cost_center", self.child.name),
                values.get("account", "Expense"),
                values.get("posting_date", "2021-01-01"),
                values.get("is_opening", "No"),
                values.get("is_cancelled", 0),
                values.get("finance_book"),
                debit,
                credit,
            ),
        )

    def test_expense_closing_balance_matches_trial_balance_example(self):
        self.add_entry(2010399929.31, 4725309.63, is_opening="Yes")
        self.add_entry(1956040390.92, 240333723.74)
        self.add_entry(35395432.30, finance_book="GYALSUNG INFRA")
        amounts = report.get_site_amounts(self.filters, [self.site])
        self.assertAlmostEqual(amounts[self.site.name][0], 3721381286.86, places=2)

    def test_opening_history_and_default_book_apply_to_all_balances(self):
        self.mock_db.get_value.return_value = "Default Book"
        for account in ["Expense", self.warehouse, report.DEFAULT_ADVANCE_ACCOUNT]:
            self.add_entry(100, account=account, posting_date="2019-12-31")
            self.add_entry(20, account=account, is_opening="Yes", finance_book="")
            self.add_entry(30, 5, account=account, finance_book="Default Book")
            self.add_entry(1000, account=account, finance_book="Other Book")
            self.add_entry(1000, account=account, posting_date="2026-09-15")
            self.add_entry(1000, account=account, is_cancelled=1)
            self.add_entry(1000, account=account, company="Other Company")
            self.add_entry(1000, account=account, cost_center="Head Office - GYALSUNG")
        amounts = report.get_site_amounts(self.filters, [self.site])
        self.assertEqual(amounts[self.site.name], [145, 145, 145])

    def test_empty_site_has_zero_balances(self):
        amounts = report.get_site_amounts(self.filters, [self.site])
        self.assertEqual(amounts[self.site.name], [0, 0, 0])

    def test_report_uses_each_parent_cost_centers_estimated_budget(self):
        sites = [
            frappe._dict(name=self.site.name, lft=1, rgt=6, estimated_budget="1250000.75"),
            frappe._dict(name="Khotokha - GYALSUNG", lft=7, rgt=12, estimated_budget=0),
            frappe._dict(name=report.HEAD_OFFICE_COST_CENTER, lft=13, rgt=18, estimated_budget=99),
        ]
        with patch.object(report.frappe, "get_all", return_value=sites) as get_all, patch.object(
            report, "get_site_amounts", return_value={site.name: [100, 20, 30] for site in sites}
        ), patch.object(report, "_", lambda text: text):
            _columns, rows, message = report.execute(self.filters)

        self.assertEqual([row["estimated_budget"] for row in rows], [1250000.75, 0, 99])
        self.assertEqual([row["budget_consumed"] for row in rows], [150, 150, 150])
        self.assertEqual(rows[2]["cost_center"], report.HEAD_OFFICE_COST_CENTER)
        self.assertIsNone(message)
        get_all.assert_called_once_with(
            "Cost Center",
            filters={
                "company": self.filters.company,
                "is_group": 1,
                "name": ["in", list(report.PARENT_WAREHOUSE_ACCOUNTS)],
            },
            fields=["name", "lft", "rgt", "estimated_budget"],
            order_by="name asc",
        )
        self.mock_db.table_exists.assert_not_called()

    def test_head_office_includes_parent_and_children_without_mixing_site_balances(self):
        head_office = frappe._dict(name=report.HEAD_OFFICE_COST_CENTER, lft=7, rgt=12)
        head_office_child = frappe._dict(name="Head Office Child", lft=8, rgt=9)
        warehouse = report.PARENT_WAREHOUSE_ACCOUNTS[head_office.name]
        self.accounts.append(frappe._dict(name=warehouse, lft=15, rgt=16, root_type="Asset"))
        self.add_entry(100)
        self.add_entry(200, cost_center=head_office.name)
        self.add_entry(50, cost_center=head_office_child.name)
        self.add_entry(30, account=warehouse, cost_center=head_office_child.name)
        self.add_entry(20, account=report.DEFAULT_ADVANCE_ACCOUNT, cost_center=head_office.name)
        self.add_entry(999, account=self.warehouse, cost_center=head_office.name)
        with patch.object(report.frappe, "get_all", side_effect=lambda doctype, **kwargs:
            [self.site, self.child, head_office, head_office_child]
            if doctype == "Cost Center" else self.accounts
        ):
            amounts = report.get_site_amounts(self.filters, [self.site, head_office])
        self.assertEqual(amounts[self.site.name], [100, 0, 0])
        self.assertEqual(amounts[head_office.name], [250, 30, 20])

    def test_actual_budget_only_includes_operating_expense_tree(self):
        self.add_entry(100, account=report.OPERATING_EXPENSE_ACCOUNT)
        self.add_entry(200, account="Expense")
        self.add_entry(50, 10, account="Nested Operating Expense")
        self.add_entry(1000, account="Non-operating Expense")
        amounts = report.get_site_amounts(self.filters, [self.site])
        self.assertEqual(amounts[self.site.name][0], 340)
