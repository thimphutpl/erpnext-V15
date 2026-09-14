import unittest
import shutil
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import frappe
from frappe.build import html_to_js_template

from erpnext.management_dashboard.page.common_dashboard import common_dashboard as dashboard


class TestCommonDashboard(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node is required to validate page JavaScript")
    def test_generated_page_script_and_template_render(self):
        folder = Path(__file__).parent
        script = (Path(frappe.__file__).parent / "public/js/frappe/microtemplate.js").read_text()
        script += html_to_js_template("common_dashboard.html", (folder / "common_dashboard.html").read_text())
        script += (folder / "common_dashboard.js").read_text()
        result = subprocess.run(
            ["node", "-e", '''
                const context = {frappe: {templates: {}, pages: {"common-dashboard": {}}}, __: text => text};
                require("vm").runInNewContext(require("fs").readFileSync(0, "utf8"), context);
                const html = context.frappe.render_template("common_dashboard");
                require("assert")(html.includes('aria-label="Estimated Budget and Total Expenses by site"'));
                require("assert")(html.includes("<iframe"));
                require("assert")(html.indexOf('class="site-budget-details') < html.indexOf('class="site-budget-chart"'));
                require("assert")(html.includes('class="site-budget-totals"'));
                require("assert")(!html.includes("<details"));
            '''],
            input=script, text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def setUp(self):
        for target, replacement in [
            ("get_report_doc", Mock()),
            ("execute", Mock()),
            ("nowdate", Mock(return_value="2026-09-14")),
            ("now_datetime", Mock(return_value="2026-09-14 16:00:00")),
            ("_", lambda text: text),
        ]:
            patcher = patch.object(dashboard, target, replacement)
            patcher.start()
            self.addCleanup(patcher.stop)
        for target, replacement in [
            ("db", Mock()),
            ("get_list", Mock(return_value=["GYALSUNG INFRA"])),
        ]:
            patcher = patch.object(dashboard.frappe, target, replacement)
            patcher.start()
            self.addCleanup(patcher.stop)
        dashboard.frappe.db.get_value.return_value = "BTN"

    def test_chart_uses_report_totals_and_preserves_missing_budgets(self):
        dashboard.execute.return_value = ([], [
            {
                "cost_center": "Gyalpozhing - GYALSUNG", "estimated_budget": None,
                "actual_annual_budget": 3721381286.86, "inventory_budget": -143734710.66,
                "advance_to_suppliers": 668221698.78, "budget_consumed": 4245868274.98,
            },
            {
                "cost_center": "Khotokha - GYALSUNG", "estimated_budget": 0,
                "actual_annual_budget": 75, "inventory_budget": -5,
                "advance_to_suppliers": 30, "budget_consumed": 100,
            },
        ], None)
        result = dashboard.get_site_budget_chart.__wrapped__()
        dashboard.get_report_doc.assert_called_once_with("Site Budget Consumption")
        dashboard.execute.assert_called_once_with({
            "company": "GYALSUNG INFRA", "from_date": "2020-01-01", "to_date": "2026-09-14",
        })
        self.assertEqual(result["currency"], "BTN")
        self.assertEqual(result["sites"][0], {
            "cost_center": "Gyalpozhing - GYALSUNG", "site": "Gyalpozhing",
            "estimated_budget": None, "total_expenses": 4245868274.98,
            "actual_expenses": 3721381286.86, "inventory_balance": -143734710.66,
            "advance_to_suppliers_balance": 668221698.78,
            "head_office_allocation": None, "head_office_allocation_percent": None,
        })
        self.assertEqual(result["sites"][1]["estimated_budget"], 0)
        self.assertEqual(result["totals"], {
            "estimated_budget": 0, "actual_expenses": 3721381361.86,
            "inventory_balance": -143734715.66, "advance_to_suppliers_balance": 668221728.78,
            "total_expenses": 4245868374.98,
            "head_office_allocation": 0,
        })

    def test_head_office_is_distributed_to_five_sites_and_included_once_in_totals(self):
        rows = [
            {
                "cost_center": name, "estimated_budget": index + 1,
                "actual_annual_budget": 100, "inventory_budget": 20,
                "advance_to_suppliers": 30, "budget_consumed": 150,
            }
            for index, name in enumerate(dashboard.SITE_WAREHOUSE_ACCOUNTS)
        ]
        rows.append({
            "cost_center": dashboard.HEAD_OFFICE_COST_CENTER, "estimated_budget": 999999,
            "actual_annual_budget": 60, "inventory_budget": 25,
            "advance_to_suppliers": 15, "budget_consumed": 100,
        })
        dashboard.execute.return_value = ([], rows, None)
        result = dashboard.get_site_budget_chart.__wrapped__()
        self.assertEqual(len(result["sites"]), 5)
        self.assertEqual([site["head_office_allocation"] for site in result["sites"]],
            [6.67, 13.33, 20, 26.67, 33.33])
        self.assertAlmostEqual(sum(site["head_office_allocation_percent"] for site in result["sites"]), 100)
        self.assertEqual(result["head_office_total_expenses"], 100)
        self.assertEqual(result["totals"]["estimated_budget"], 15)
        self.assertEqual(result["totals"]["head_office_allocation"], 100)
        self.assertEqual(result["totals"]["total_expenses"], 850)
        self.assertEqual(result["sites"][0]["total_expenses"], 156.67)
        self.assertIsNone(result["allocation_message"])

    def test_allocation_handles_zero_missing_and_negative_budgets(self):
        sites = [{"estimated_budget": budget, "total_expenses": 10} for budget in [100, 0, None]]
        message = dashboard.allocate_head_office_expenses(sites, 50)
        self.assertEqual([site["head_office_allocation"] for site in sites], [50, 0, 0])
        self.assertIn("zero or missing", message)
        for budgets in ([0, None], [100, -10]):
            sites = [{"estimated_budget": budget, "total_expenses": 10} for budget in budgets]
            message = dashboard.allocate_head_office_expenses(sites, 50)
            self.assertTrue(message)
            self.assertTrue(all(site["head_office_allocation"] is None for site in sites))
            self.assertTrue(all(site["total_expenses"] == 10 for site in sites))

    def test_allocation_reconciles_rounding_and_head_office_credits(self):
        for total, expected in [(0.01, [0.01, 0, 0, 0, 0]), (-0.01, [0, 0, 0, 0, -0.01])]:
            sites = [{"estimated_budget": 1, "total_expenses": 10} for _ in range(5)]
            dashboard.allocate_head_office_expenses(sites, total)
            self.assertEqual([site["head_office_allocation"] for site in sites], expected)
            self.assertAlmostEqual(sum(site["total_expenses"] for site in sites), 50 + total)

    def test_report_permission_is_checked_before_reading_financial_data(self):
        dashboard.get_report_doc.side_effect = frappe.PermissionError
        with self.assertRaises(frappe.PermissionError):
            dashboard.get_site_budget_chart.__wrapped__()
        dashboard.execute.assert_not_called()
        dashboard.frappe.get_list.assert_not_called()

    def test_company_permission_is_checked_before_reading_financial_data(self):
        dashboard.frappe.get_list.return_value = []
        with patch.object(dashboard, "_", lambda text: text), patch.object(
            dashboard.frappe, "throw", side_effect=frappe.PermissionError
        ):
            with self.assertRaises(frappe.PermissionError):
                dashboard.get_site_budget_chart.__wrapped__()
        dashboard.execute.assert_not_called()
