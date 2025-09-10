# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AbstractBillItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link
		activity_head: DF.Data | None
		amount: DF.Currency
		base_amount: DF.Currency
		bill_date: DF.Date | None
		bill_no: DF.Data | None
		business_activity: DF.Link
		cash_receipt: DF.Currency
		cost_center: DF.Link
		narration: DF.SmallText | None
		not_required: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		party: DF.DynamicLink
		party_type: DF.Literal["", "Supplier", "Employee", "Agency", "Beneficiary"]
		reference_name: DF.DynamicLink | None
		reference_type: DF.Link | None
		reimburse_amount: DF.Currency
		remarks: DF.SmallText | None
		tax_exempted: DF.Check
	# end: auto-generated types
	pass
