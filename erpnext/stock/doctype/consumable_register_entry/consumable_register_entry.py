# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ConsumableRegisterEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		date: DF.Date
		issued_to: DF.Link
		item_code: DF.Link
		qty: DF.Data
		ref_doc: DF.Data | None
	# end: auto-generated types
	pass
