# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DHIGCOA(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account_code: DF.Data
		account_name: DF.Data
		account_type: DF.Literal["", "Bank", "Cash", "Depreciation", "Tax", "Chargeable", "Warehouse", "Receivable", "Payable", "Equity", "Fixed Asset", "Cost of Goods Sold", "Expense Account", "Round Off", "Income Account", "Stock Received But Not Billed", "Expenses Included In Valuation", "Stock Adjustment", "Stock", "Temporary", "Capital Work in Progress"]
		is_inter_company: DF.Check
		root_type: DF.Literal["", "Asset", "Liability", "Income", "Expense", "Equity"]
	# end: auto-generated types
	pass
