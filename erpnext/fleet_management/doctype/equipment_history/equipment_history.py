# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class EquipmentHistory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account_number: DF.Data | None
		bank_name: DF.Data | None
		branch: DF.Link
		from_date: DF.Date | None
		ifs_code: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		reference_document: DF.Data | None
		supplier: DF.Link | None
		to_date: DF.Date | None
	# end: auto-generated types
	pass
