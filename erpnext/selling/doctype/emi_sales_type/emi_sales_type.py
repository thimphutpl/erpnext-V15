# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class EMISalesType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.selling.doctype.emi_sales_type_item.emi_sales_type_item import EMISalesTypeItem
		from frappe.types import DF

		company: DF.Link | None
		customer_group: DF.Table[EMISalesTypeItem]
		disabled: DF.Check
		enable_cost_sharing: DF.Check
		order_type_code: DF.Data
		order_type_name: DF.Data
		required_commission: DF.Check
		restrict: DF.Check
	# end: auto-generated types
	pass
