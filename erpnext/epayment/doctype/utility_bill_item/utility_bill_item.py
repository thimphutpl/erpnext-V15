# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class UtilityBillItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		consumer_code: DF.Data | None
		cost_center: DF.Data | None
		create_direct_payment: DF.Check
		debit_account: DF.Link
		fetch_status_code: DF.Data | None
		invoice_amount: DF.Currency
		invoice_date: DF.Date | None
		invoice_no: DF.Data | None
		net_amount: DF.Currency
		outstanding_amount: DF.Currency
		outstanding_datetime: DF.Datetime | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		party: DF.Link
		payment_journal_no: DF.Data | None
		payment_response_msg: DF.SmallText | None
		payment_status: DF.Literal["In Progress", "Pending", "Success", "Failed"]
		payment_status_code: DF.Data | None
		pi_number: DF.Data | None
		request: DF.SmallText | None
		response: DF.SmallText | None
		response_msg: DF.SmallText | None
		tds_amount: DF.Currency
		tds_applicable: DF.Check
		utility_service_type: DF.Link
	# end: auto-generated types
	pass
