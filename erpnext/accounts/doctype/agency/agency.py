# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Agency(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account_number: DF.Data | None
		agency_name: DF.Data
		bank: DF.Data | None
		bank_ac_no: DF.Data | None
		bank_account_type: DF.Link | None
		bank_address: DF.Data | None
		bank_branch: DF.Link | None
		bank_name: DF.Link | None
		swift_code: DF.Data | None
	# end: auto-generated types
	pass
