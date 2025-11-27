# -*- coding: utf-8 -*-
# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states

class EMISalesCancellation(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.selling.doctype.emi_sales_cancellation_item.emi_sales_cancellation_item import EMISalesCancellationItem
		from frappe.types import DF

		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Link | None
		approver_name: DF.Data | None
		items: DF.Table[EMISalesCancellationItem]
		posting_date: DF.Date | None
		reason: DF.Literal["", "Amount Mismatch", "Date Mismatch", "Customer Code", "Material Code", "Return of Trading Goods", "Cost Center", "Warehouse", "Incorrect Order Type", "Double Sales Order"]
		reason_for_rejection: DF.Data | None
		region: DF.Link | None
		requested_by: DF.Link | None
		requested_by_name: DF.Data | None
	# end: auto-generated types
	def validate(self):
		self.validate_owner()
		self.validate_duplicate()
		if self.workflow_state == "Rejected":
			if not self.reason_for_rejection:
				frappe.throw("Reason for Rejection is Mandatory")
		else:
			self.reason_for_rejection = None
		validate_workflow_states(self)
		# if self.workflow_state != "Approved":
		# 	notify_workflow_states(self)

	def before_cancel(self):
		# if frappe.session.user != "Administrator":
		frappe.throw("Cannot Cancel")

	def validate_duplicate(self):
		row = 1
		for item in self.items:
			if len(frappe.db.sql("""
						select a.name from `tabEMI Sales Cancellation` a, `tabEMI Sales Cancellation Item` b where a.docstatus < 2
						and b.parent = a.name and b.btl_sales = '{}' and a.name != '{}'
						""".format(item.btl_sales.upper(), self.name))) > 0:
						frappe.throw("EMI Sales Cancellation Request already exists for Sales Order {} in row {}".format(item.btl_sales, row))
			if frappe.db.get_value("EMI Sales", item.btl_sales, "docstatus") in  (2, 0):
				frappe.throw("Cannot request EMI Sales {} in row {} since it is either in draft or already cancelled.".format(item.btl_sales, row))
			row += 1

	def validate_owner(self):
		row = 1
		for a in self.items:
			doc = frappe.get_doc("EMI Sales", a.btl_sales.upper())
			if not doc:
				frappe.throw("Sales Order {} doesn't exist in row {}.".format(a.btl_sales, row))
			if doc.owner != self.owner:
				frappe.throw("You cannot cancel {} in row {} since owner of BT Sales document is different.".format(a.btl_sales, row))
			row += 1

	def on_submit(self):
		for a in self.items:
			doc = frappe.get_doc("EMI Sales", a.btl_sales)
			doc.flags.ignore_permissions = 1
			doc.cancel()
		notify_workflow_states(self)

	def check_employee(self):
		if not frappe.db.exists("Employee", {"user_id": self.owner}):
			frappe.throw("The owner of this document i.e. {} is not registered as an Employee!".format(self.owner))

@frappe.whitelist()
def get_permission_query_conditions(user):
	# restrick user from accessing this doctype
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator":
		return
	if "Sales Master" in user_roles or "System Manager" in user_roles:
		return

	return """(
		`tabEMI Sales Cancellation`.owner = '{user}'
		or
		(`tabEMI Sales Cancellation`.approver = '{user}' and `tabEMI Sales Cancellation`.workflow_state not in  ('Draft','Approved','Rejected','Cancelled'))
		)""".format(user=user)