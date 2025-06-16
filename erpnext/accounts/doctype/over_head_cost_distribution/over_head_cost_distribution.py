# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class OverHeadCostDistribution(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.over_head_cost_item.over_head_cost_item import OverHeadCostItem
		from frappe.types import DF

		account: DF.Link
		amended_from: DF.Link | None
		distribution_type: DF.Literal["Cost Center to Cost Center", "Cost Center to Project"]
		items: DF.Table[OverHeadCostItem]
		source_branch: DF.Link
		source_cost_center: DF.Link | None
		source_total_amount: DF.Currency
	# end: auto-generated types
	pass
