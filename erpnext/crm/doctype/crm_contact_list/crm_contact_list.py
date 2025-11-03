# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CRMContactList(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		company: DF.Link | None
		country: DF.Link | None
		dzongkhag: DF.Link | None
		email: DF.Data | None
		enable: DF.Check
		exact_location: DF.Data | None
		fax: DF.Data | None
		focal_name: DF.Data
		mobile_number: DF.Data | None
		telephone: DF.Data | None
	# end: auto-generated types
	pass
