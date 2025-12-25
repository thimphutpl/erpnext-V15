# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class VoucherCorectionDetail(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		child_row_idx: DF.Data | None
		child_table: DF.Literal["", "accounts", "taxes", "items"]
		field_name: DF.Literal["", "cost_center", "cheque_no", "posting_date", "account_head", "party_type", "party", "paid_from"]
		new_value: DF.Data | None
		old_value: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		scope: DF.Literal["", "Header", "Child"]
	# end: auto-generated types
	pass
