# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class EMIPaymentSchedule(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		beginning_balance: DF.Currency
		due_date: DF.Date | None
		ending_balance: DF.Currency
		interest: DF.Currency
		mode_of_payment: DF.Link | None
		paid_amount: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		payable_amount: DF.Currency
		payment_date: DF.Date | None
		principal: DF.Currency
		reference: DF.Link | None
		status: DF.Literal["", "Paid", "Unpaid"]
	# end: auto-generated types
	pass
