# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from frappe.utils import (
	add_days,
	ceil,
	cint,
	cstr,
	date_diff,
	floor,
	flt,
	formatdate,
	get_first_day,
	get_last_day,
	get_link_to_form,
	getdate,
	money_in_words,
	rounded,
	nowdate
)

class VisitorPassRegistry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.event_management.doctype.visitor_pass_other_charges.visitor_pass_other_charges import VisitorPassOtherCharges
		from erpnext.event_management.doctype.visitor_pass_registry_detail.visitor_pass_registry_detail import VisitorPassRegistryDetail
		from erpnext.event_management.doctype.visitor_pass_registry_item.visitor_pass_registry_item import VisitorPassRegistryItem
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		cashier: DF.Link
		company: DF.Link | None
		cost_center: DF.Link | None
		grand_total: DF.Currency
		items: DF.Table[VisitorPassRegistryItem]
		journal_entry: DF.Data | None
		location: DF.Link
		other_charges: DF.Table[VisitorPassOtherCharges]
		posting_date: DF.Date
		remarks: DF.SmallText | None
		status: DF.Literal["Draft", "Open", "Closed", "Submitted", "Cancelled"]
		total_amount: DF.Currency
		total_csr_amount: DF.Currency
		total_visitors: DF.Int
		transaction_details: DF.Table[VisitorPassRegistryDetail]
	# end: auto-generated types
	
	def validate(self):
		self.set_status()
		self.validate_amount()
		self.validate_transaction_details()

	def update_status(self, status):
		self.set_status(update=True, status=status)

	def on_cancel(self):
		self.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry")

	def set_status(self, update=False, status=None, update_modified=True):
		if self.is_new():
			if self.get("amended_from"):
				self.status = "Draft"
			return

		if not status:
			if self.docstatus == 2:
				status = "Cancelled"
			elif self.docstatus == 1:
				self.status = "Open"
		else:
			self.status = status

		if update:
			self.db_set("status", self.status, update_modified=update_modified)

	def validate_amount(self):
		total_amount, total_visitor = 0.0, 0
		for d in self.items:
			d.amount = flt(d.qty) * flt(d.ticket_price)
			total_amount += flt(d.amount)
			total_visitor += flt(d.qty)
		self.total_visitors = total_visitor
		self.total_amount = flt(total_amount)

		oc_total = 0.0
		for oc in self.other_charges:
			oc_total += flt(oc.amount)
		self.total_amount += flt(oc_total)

		self.grand_total = flt(self.total_amount)

	def validate_transaction_details(self):
		payments = []
		for d in self.get("items"):
			existing_pay = [pay for pay in payments if pay.mode_of_payment == d.mode_of_payment]
			if existing_pay:
				existing_pay[0].amount += flt(d.amount)
			else:
				payments.append(
					frappe._dict(
						{
							"mode_of_payment": d.mode_of_payment,
							"amount": d.amount,
						}
					)
				)

		for oc in self.get("other_charges"):
			existing_pay = [pay for pay in payments if pay.mode_of_payment == oc.mode_of_payment]
			if existing_pay:
				existing_pay[0].amount += flt(oc.amount)
			else:
				payments.append(
					frappe._dict(
						{
							"mode_of_payment": oc.mode_of_payment,
							"amount": oc.amount,
						}
					)
				)

		self.set("transaction_details", payments)

	# @frappe.whitelist()
	# def add_other_charges(self, fee_type, qty, mode_of_payment):
	# 	fee_type_doc = frappe.get_doc("Fee Type", fee_type)
	# 	if not fee_type_doc:
	# 		frappe.throw(_("Fee Type not found"))
		
	# 	rate = fee_type_doc.rate
	# 	if not rate:
	# 		frappe.throw(_("Rate not found for the selected Fee Type"))

	# 	amount = qty * rate

	# 	self.append("other_charges", {
	# 		"fee_type": fee_type,
	# 		"qty": qty,
	# 		"rate": rate,
	# 		"mode_of_payment": mode_of_payment,
	# 		"amount": amount
	# 	})

	# 	self.save()

	# 	return _("Other Charges Added Successfully!")

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_cashiers(doctype, txt, searchfield, start, page_len, filters):
	cashiers_list = frappe.get_all("Event Profile User", filters=filters, fields=["user"], as_list=1)
	return [c for c in cashiers_list]


@frappe.whitelist()
def get_mode_of_payment(doctype, txt, searchfield, start, page_len, filters):
	payment_list = frappe.get_all("Event Payment Method", filters=filters, fields=["mode_of_payment"], as_list=1)
	return [c for c in payment_list]

# @frappe.whitelist()
# def update_status(status, name):
# 	doc = frappe.get_doc("Visitor Pass Registry", name)
# 	doc.post_journal_entry()
# 	doc.update_status(status)

