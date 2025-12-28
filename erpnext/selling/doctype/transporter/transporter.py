# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Transporter(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account_number: DF.Data | None
		amended_from: DF.Link | None
		bank_account_type: DF.Link | None
		bank_branch: DF.Link | None
		bank_name: DF.Link | None
		blacklist: DF.Check
		dzongkhag: DF.Link | None
		enabled: DF.Check
		mobile_no: DF.Int
		telephone_and_fax: DF.Data | None
		tpn_no: DF.Data | None
		transport_request: DF.Link | None
		transporter_id: DF.Data
		transporter_name: DF.Data
		user: DF.Link | None
	# end: auto-generated types
	pass
