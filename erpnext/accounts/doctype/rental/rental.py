# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
# import frappe
from frappe.model.document import Document
import frappe
from frappe.utils import flt
from erpnext.custom_utils import prepare_gl
class Rental(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.model.document import Document
		from frappe.types import DF

		account_head: DF.Data | None
		amended_from: DF.Link | None
		branch: DF.Link
		company: DF.Data | None
		cost_center: DF.Link | None
		gst_amount: DF.Currency
		posting_date: DF.Date
		rental_details: DF.Table[Document]
		tax_rate: DF.Float
		taxes_and_charges: DF.Data | None
		total_amount: DF.Float
		total_gst_amount: DF.Currency
	# end: auto-generated types
	pass
	def before_save(self):
		template_name = "GST 5% Outward - CDCL"
		
		# Get taxes for the template
		taxes = self.get_taxes_for_template(template_name)	
		if taxes:
			tax = taxes[0]  # first row from template
			
			self.taxes_and_charges = template_name
			self.account_head = tax.get("account_head")
			self.tax_rate = tax.get("rate") or 0
			
			# Calculate GST
			self.gst_amount = (self.total_amount or 0) * self.tax_rate / 100
			self.total_gst_amount = (self.total_amount or 0) + self.gst_amount
	def on_submit(self):
		self.update_general_ledger()		

	def get_taxes_for_template(self, template_name):
		"""Get tax details from a Sales Taxes and Charges Template"""
		return frappe.get_all(
			"Sales Taxes and Charges",
			filters={"parent": template_name},
			fields=["charge_type", "account_head", "rate", "description"]
		)
	def update_general_ledger(self):
		gl_entries = []

		rental_account = frappe.db.get_value("Company", self.company, "rental_account")
		default_receivable_account = frappe.db.get_value("Branch", self.branch, "revenue_bank_account")
		if rental_account:
			gl_entries.append(
				prepare_gl(self, {
					"account": rental_account,
					"credit": flt(self.total_amount),
					"credit_in_account_currency": flt(self.total_amount),
					"cost_center": self.cost_center,
			
				})
			)
			gl_entries.append(
				prepare_gl(self, {
					"account": self.account_head,
					"credit": flt(self.gst_amount),
					"credit_in_account_currency": flt(self.gst_amount),
					"cost_center": self.cost_center,
				
				})
			)
			gl_entries.append(
				prepare_gl(self, {
					"account": default_receivable_account,
					"debit": flt(self.total_gst_amount),
					"debit_in_account_currency": flt(self.total_gst_amount),
					"cost_center": self.cost_center,
				
				})
			)
			

			
		

		if gl_entries:
			from erpnext.accounts.general_ledger import make_gl_entries
			make_gl_entries(gl_entries, cancel=(self.docstatus == 2), merge_entries=False)
