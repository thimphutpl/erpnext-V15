# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class UtilityServiceType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		abbr: DF.Data | None
		company: DF.Link
		expense_account: DF.Link | None
		fetch_outstanding_api: DF.Link
		fetch_outstanding_api_link: DF.Data | None
		party: DF.Link
		payment_api: DF.Link
		payment_api_link: DF.Data | None
		service_id: DF.Data
		service_name: DF.Data | None
		service_type: DF.Data
		unique_key_field: DF.Data
	# end: auto-generated types

	pass
