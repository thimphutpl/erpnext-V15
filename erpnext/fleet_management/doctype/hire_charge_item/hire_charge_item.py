# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HireChargeItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from_date: DF.Date | None
		idle_rate_external: DF.Currency
		idle_rate_internal: DF.Currency
		main_int: DF.Float
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		perf_bench: DF.Int
		rate_broadleaf_external: DF.Currency
		rate_broadleaf_internal: DF.Currency
		rate_conifer_external: DF.Currency
		rate_conifer_internal: DF.Currency
		rate_fuel_external: DF.Currency
		rate_fuel_internal: DF.Currency
		rate_wofuel_external: DF.Currency
		rate_wofuel_internal: DF.Currency
		to_date: DF.Date | None
		yard_distance: DF.Float
		yard_hours: DF.Float
	# end: auto-generated types
	pass
