# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ChangeStatus(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link | None
		capacity: DF.Data | None
		customer: DF.Data | None
		delivery_note: DF.Data | None
		posting_date: DF.Date | None
		status_to: DF.Literal["", "Remove From Queue", "Confirm Delivery", "Cancel"]
		transaction_no: DF.DynamicLink | None
		transaction_type: DF.Literal["", "Load Request", "Delivery Confirmation"]
		vehicle: DF.Data | None
	# end: auto-generated types
	def validate(self):
		self.capacity = frappe.db.get_value("Vehicle", self.vehicle, "vehicle_capacity")


	def on_submit(self):
		doc = frappe.get_doc(self.transaction_type, self.transaction_no)
		if self.transaction_type == "Load Request":
			frappe.db.sql("update `tabLoad Request` set load_status = 'Cancelled', docstatus = 2 where name = '{0}'".format(self.transaction_no))
			#doc.load_status = "Cancelled"
			#doc.docstatus = 2
		else:
			if self.status_to == "Cancel":
				frappe.db.sql("update `tabDelivery Confirmation` set confirmation_status = 'Cancelled', docstatus = 2 where name = '{0}'".format(self.transaction_no))
				#doc.confirmation_status = "Cancelled"
				#doc.docstatus = 2
			else:	
				doc.confirmation_status = "Received"
				doc.save(ignore_permissions = True)
