# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class EMISalesItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		actual_qty: DF.Float
		allow_zero_valuation_rate: DF.Check
		amount: DF.Currency
		base_amount: DF.Currency
		business_activity: DF.Link
		cash_bank_account: DF.Link | None
		commission_account: DF.Link | None
		commission_amount: DF.Currency
		commission_percent: DF.Percent
		conversion_factor: DF.Data | None
		cost_center: DF.Link | None
		data_package: DF.Currency
		description: DF.SmallText | None
		discount_account: DF.Link | None
		discount_amount: DF.Currency
		discount_percent: DF.Currency
		expense_account: DF.Link | None
		ime_number: DF.Data | None
		ime_number_ii: DF.Data | None
		income_account: DF.Link | None
		interest_amount: DF.Currency
		is_foc_item: DF.Check
		item_code: DF.Link
		item_group: DF.Link | None
		item_name: DF.Data | None
		item_subgroup: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		prepaid_expense_account: DF.Link | None
		prepaid_income_account: DF.Link | None
		purchase_limit: DF.Currency
		qty: DF.Float
		rate: DF.Currency
		selling_price: DF.Link | None
		serial_number: DF.Data | None
		sim_type: DF.Literal["", "NEW SIM", "SIM REPLACEMENT", "SIM RECONNECTION"]
		so_detail: DF.Data | None
		stock_qty: DF.Data | None
		stock_uom: DF.Data | None
		target_warehouse: DF.Link | None
		taxable_amount: DF.Currency
		taxable_percent: DF.Percent
		tds_account: DF.Link | None
		tds_amount: DF.Currency
		tds_deducted_by_customer: DF.Currency
		tds_deducted_by_customer_account: DF.Link | None
		tds_percent: DF.Percent
		to_serial_number: DF.Data | None
		total_amount_received: DF.Currency
		total_data_package: DF.Currency
		uom: DF.Link | None
		warehouse: DF.Link | None
	# end: auto-generated types
	pass
