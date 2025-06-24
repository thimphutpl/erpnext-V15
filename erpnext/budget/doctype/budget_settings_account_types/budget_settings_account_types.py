# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class BudgetSettingsAccountTypes(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account_type: DF.Literal["", "Accumulated Depreciation", "Asset Received But Not Billed", "Bank", "Cash", "Chargeable", "Capital Work in Progress", "Cost of Goods Sold", "Depreciation", "Equity", "Expense Account", "Expenses Included In Asset Valuation", "Expenses Included In Valuation", "Fixed Asset", "Income Account", "Payable", "Receivable", "Round Off", "Stock", "Stock Adjustment", "Stock Received But Not Billed", "Service Received But Not Billed", "Tax", "Temporary"]
		name: DF.Int | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types
	pass
