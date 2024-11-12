# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class RevenueTargetAccount(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link
		account_number: DF.Data | None
		adjustment_amount: DF.Currency
		april: DF.Currency
		august: DF.Currency
		branch: DF.Link
		cost_center: DF.Link | None
		december: DF.Currency
		february: DF.Currency
		january: DF.Currency
		july: DF.Currency
		june: DF.Currency
		march: DF.Currency
		may: DF.Currency
		net_target_amount: DF.Currency
		november: DF.Currency
		october: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		reference: DF.Data | None
		reference_item: DF.Data | None
		september: DF.Currency
		target_amount: DF.Currency
	# end: auto-generated types
	pass
