# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TimberClass(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.production.doctype.royal_rate.royal_rate import RoyalRate
		from frappe.types import DF

		class_name: DF.Data
		items: DF.Table[RoyalRate]
	# end: auto-generated types
	pass
