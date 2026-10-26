# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest
from contextlib import ExitStack
from unittest.mock import Mock, patch

import frappe

from erpnext.stock.doctype.material_return.material_return import MaterialReturn


MODULE = "erpnext.stock.doctype.material_return.material_return"


class TestMaterialReturn(unittest.TestCase):
	def setUp(self):
		stack = ExitStack()
		self.addCleanup(stack.close)
		# Build an in-memory voucher without loading site metadata or writing ledgers.
		self.doc = MaterialReturn.__new__(MaterialReturn)
		self.doc.__dict__.update(
			doctype="Material Return",
			name="MRE-2942",
			company="_Test Company",
			posting_date="2025-09-29",
			docstatus=1,
			cost_center="Warehouse Cost Center",
			items=[
				frappe._dict(
					name="return-row",
					item_code="101301",
					item_name="Test Item",
					warehouse="Test Warehouse",
					expense_account="Expense Account",
					project_cost_center="Project Cost Center",
					project="Test Project",
					amount=2437.43,
				)
			],
		)
		self.sle_map = {"return-row": [frappe._dict(stock_value_difference=2438.8)]}
		self.doc.get_stock_ledger_details = Mock(return_value=self.sle_map)
		self.doc.get_debit_field_precision = Mock(return_value=2)
		self.warehouse_account = {"Test Warehouse": {"account": "Warehouse Account"}}
		self.db = stack.enter_context(patch.object(frappe, "db", new=Mock()))
		self.db.get_value.side_effect = lambda doctype, *args: {
			"Company": "Adjustment Account",
			"Warehouse": "Warehouse Account",
		}[doctype]
		stack.enter_context(patch("erpnext.custom_utils.get_fiscal_year", return_value=["2025"]))
		stack.enter_context(patch.object(frappe, "get_system_settings", return_value="Banker's Rounding"))

	def test_repost_preserves_return_accounts_and_cost_centers(self):
		# Material Return Item has project_cost_center, but no cost_center field.
		entries = self.doc.get_gl_entries(self.warehouse_account)

		self.assertEqual(
			[(d.account, d.cost_center, d.project, d.debit, d.credit) for d in entries],
			[
				("Expense Account", "Project Cost Center", "Test Project", 0, 2438.8),
				("Adjustment Account", "Project Cost Center", "Test Project", 2438.8, 0),
				("Warehouse Account", "Warehouse Cost Center", "", 2438.8, 0),
				("Adjustment Account", "Warehouse Cost Center", "", 0, 2438.8),
			],
		)
		self.assertEqual(sum(d.debit - d.credit for d in entries), 0)
		self.assertEqual(self.doc.items[0].amount, 2437.43)
		for entry in entries:
			self.assertEqual(entry.voucher_type, "Material Return")
			self.assertEqual(entry.voucher_no, "MRE-2942")
			self.assertEqual(entry.debit, entry.debit_in_account_currency)
			self.assertEqual(entry.credit, entry.credit_in_account_currency)

	def test_repost_uses_each_voucher_detail_and_rounds_stock_value(self):
		second_row = self.doc.items[0].copy()
		second_row.update(name="second-row", project_cost_center="Second Project Cost Center")
		self.doc.items.append(second_row)
		self.sle_map["return-row"] = [
			frappe._dict(stock_value_difference=2400),
			frappe._dict(stock_value_difference=38.804),
		]
		self.sle_map["second-row"] = [frappe._dict(stock_value_difference=100)]

		entries = self.doc.get_gl_entries(self.warehouse_account)

		self.assertEqual(len(entries), 8)
		self.assertEqual(entries[0].credit, 2438.8)
		self.assertEqual(entries[4].credit, 100)
		self.assertEqual(entries[4].cost_center, "Second Project Cost Center")

	def test_repost_does_not_fall_back_to_old_amount_for_zero_stock_value(self):
		self.sle_map["return-row"][0].stock_value_difference = 0

		entries = self.doc.get_gl_entries(self.warehouse_account)

		self.assertEqual(len(entries), 4)
		self.assertTrue(all(d.debit == d.credit == 0 for d in entries))

	def test_repost_skips_items_without_active_stock_ledger_entries(self):
		self.sle_map.clear()
		self.assertEqual(self.doc.get_gl_entries(self.warehouse_account), [])

	def test_repost_can_resolve_warehouse_account_without_map(self):
		entries = self.doc.get_gl_entries()
		self.assertEqual(entries[2].account, "Warehouse Account")

	def test_submission_and_cancellation_keep_document_amount(self):
		with patch(f"{MODULE}.make_gl_entries") as post_entries:
			for docstatus in (1, 2):
				with self.subTest(docstatus=docstatus):
					self.doc.docstatus = docstatus
					self.doc.make_gl_entry()

					args, kwargs = post_entries.call_args
					self.assertEqual(len(args[0]), 4)
					self.assertEqual(args[0][0].credit, 2437.43)
					self.assertEqual(kwargs["cancel"], docstatus == 2)
					self.assertFalse(kwargs["merge_entries"])
					self.assertFalse(kwargs["from_repost"])

	def test_repost_posts_supplied_entries_without_merging_adjustment_legs(self):
		entries = self.doc.get_gl_entries(self.warehouse_account)
		with patch(f"{MODULE}.make_gl_entries") as post_entries:
			self.doc.make_gl_entries(gl_entries=entries, from_repost=True)

		post_entries.assert_called_once_with(
			entries, cancel=False, update_outstanding="No", merge_entries=False, from_repost=True
		)
