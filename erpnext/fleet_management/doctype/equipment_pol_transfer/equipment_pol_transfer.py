# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EquipmentPOLTransfer(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		company: DF.Link
		fe_number: DF.ReadOnly | None
		from_branch: DF.ReadOnly | None
		from_equipment: DF.Link
		item_name: DF.Data | None
		pol_type: DF.Link
		posting_date: DF.Date
		posting_time: DF.Time
		qty: DF.Float
		remarks: DF.SmallText | None
		te_number: DF.ReadOnly | None
		to_branch: DF.ReadOnly | None
		to_equipment: DF.Link
	# end: auto-generated types
	pass
