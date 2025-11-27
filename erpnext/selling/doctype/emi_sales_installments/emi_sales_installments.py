# -*- coding: utf-8 -*-
# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class EMISalesInstallments(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		begining_balance: DF.Currency
		ending_balance: DF.Currency
		fiscal_year: DF.Link | None
		interest: DF.Currency
		month: DF.Date | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		principal: DF.Currency
		recharge_amount: DF.Currency
		reference_documents: DF.Data | None
	# end: auto-generated types
	pass
