# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AssetLifeExtension(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		additional_life: DF.Int
		amended_from: DF.Link | None
		asset: DF.Link
		asset_category: DF.ReadOnly | None
		asset_name: DF.Data | None
		branch: DF.Link | None
		company: DF.Link | None
		cost_center: DF.Link | None
		credit_account: DF.Link | None
		current_asset_value: DF.Currency
		date: DF.Date
		difference_amount: DF.Currency
		finance_book: DF.Link | None
		fixed_asset_account: DF.Link | None
		journal_entry: DF.Link | None
		new_asset_value: DF.Currency
		new_remaining_dep: DF.Float
		old_remaining_dep: DF.Float
		re_valued: DF.Check
	# end: auto-generated types
	pass
