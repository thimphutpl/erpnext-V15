# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HSDPayment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.hsd_payment_item.hsd_payment_item import HSDPaymentItem
		from frappe.types import DF

		actual_amount: DF.Currency
		amended_from: DF.Link | None
		amount: DF.Currency
		assign_from_cheque_lot: DF.Check
		bank_account: DF.Link
		bank_payment: DF.Data | None
		branch: DF.Link
		cheque__no: DF.Data | None
		cheque_date: DF.Date | None
		cheque_lot: DF.Link | None
		clearance_date: DF.Date | None
		company: DF.Link
		cost_center: DF.Link
		final_setlement: DF.Check
		fuelbook: DF.Link
		items: DF.Table[HSDPaymentItem]
		payment_status: DF.Data | None
		posting_date: DF.Date
		remarks: DF.SmallText | None
		status: DF.Literal["Draft", "Submitted", "Cancelled"]
		supplier: DF.Link
	# end: auto-generated types
	pass
