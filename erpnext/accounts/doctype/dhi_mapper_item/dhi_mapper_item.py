# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DHIMapperItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link
		account_type: DF.Data | None
		doc_company: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		root_type: DF.Data | None
	# end: auto-generated types
	pass
