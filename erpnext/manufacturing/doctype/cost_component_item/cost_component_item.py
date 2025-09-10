# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CostComponentItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		cost_component: DF.Link | None
		hour: DF.Float
		labor_cost: DF.Currency
		manufacturing_overhead: DF.ReadOnly | None
		overhead_cost: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		percent: DF.Percent
		rate_per_unit: DF.ReadOnly | None
		uom: DF.ReadOnly | None
	# end: auto-generated types
	pass
