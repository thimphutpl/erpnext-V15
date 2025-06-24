# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TDSRemittanceItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		bill_amount: DF.Currency
		bill_date: DF.Date | None
		bill_no: DF.Data | None
		business_activity: DF.Link | None
		cost_center: DF.Link | None
		invoice_no: DF.DynamicLink | None
		invoice_type: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		party: DF.DynamicLink | None
		party_name: DF.Data | None
		party_type: DF.Literal["", "Customer", "Supplier", "Employee"]
		posting_date: DF.Date | None
		tax_account: DF.Link | None
		tds_amount: DF.Currency
		tds_remittance: DF.Link | None
		tpn: DF.Data | None
	# end: auto-generated types
	pass
