# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, flt
from frappe.model.document import Document

class DepositEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.deposit_entry_item.deposit_entry_item import DepositEntryItem
		from frappe.types import DF

		amended_from: DF.Link | None
		bank_account: DF.Link
		branch: DF.Link
		cash_account: DF.Link
		company: DF.Link | None
		cost_center: DF.Link | None
		from_date: DF.Date | None
		items: DF.Table[DepositEntryItem]
		pos_profile: DF.Link
		posting_date: DF.Date
		remarks: DF.SmallText | None
		to_date: DF.Date | None
		total_amount: DF.Currency
	# end: auto-generated types
	
	def validate(self):
		self.calculate_total()

	def on_submit(self):
		self.post_gl_entry_for_cash()
		self.update_pos_closting_entry()

	def on_cancel(self):
		self.update_pos_closting_entry(cancel=True)
		self.delete_gl_enteries()

	def calculate_total(self):
		total = 0
		for d in self.items:
			total += flt(d.cash_amount)
		self.total_amount = total

	def post_gl_entry_for_cash(self):
		gl_entries = []
		for item in self.items:
			gl_entries.append(frappe._dict(
				{
					"account": self.cash_account,
					"credit": flt(item.cash_amount),
					"cost_center": self.cost_center,
					"company":self.company,
					"voucher_type":'POS Closing Entry',
					"voucher_no":item.pos_closing_entry,
					"posting_date":self.posting_date
				}))

			gl_entries.append(frappe._dict(
				{
					"account": self.bank_account,
					"debit": flt(item.cash_amount),
					"cost_center": self.cost_center,
					"company":self.company,
					"voucher_type":'POS Closing Entry',
					"voucher_no":item.pos_closing_entry,
					"posting_date":self.posting_date
				}))
		from erpnext.accounts.general_ledger import make_gl_entries
		make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=False, from_repost=False)

	def delete_gl_enteries(self):
		for item in self.items:
			frappe.db.sql("""delete from `tabGL Entry` where voucher_type='POS Closing Voucher' and voucher_no=%s""",
				(item.pos_closing_entry))

	def update_pos_closting_entry(self, cancel=False):
		for d in self.items:
			doc = frappe.get_doc('POS Closing Entry', d.pos_closing_entry)
			if cancel:
				doc.status = 'Submitted'
			else:
				doc.status = 'Deposited'
			doc.save()

	@frappe.whitelist()
	def get_pos_closing(self):
		if not self.pos_profile:
			frappe.msgprint('POS Profile is mandatory',raise_exception=1)

		if getdate(self.from_date) > getdate(self.to_date):
			frappe.msgprint('From Date cannot be after To Date',raise_exception=1)

		query = """
				SELECT 
					t1.name as pos_closing_entry,
					t2.closing_amount as cash_amount,
					t1.posting_date,
					t1.user as cashier
				FROM 
					`tabPOS Closing Entry` t1
				INNER JOIN
					`tabPOS Closing Entry Detail` t2
					ON t1.name = t2.parent
				WHERE 
					t2.mode_of_payment = %s
					AND t1.pos_profile = %s
					AND t1.posting_date BETWEEN %s AND %s
					AND t1.status = 'Submitted'
					AND NOT EXISTS (
						SELECT 1 FROM `tabDeposit Entry Item` 
						WHERE pos_closing_entry = t1.name 
						AND parent != %s
						AND docstatus = 1
					) 
				"""
		params = ('Cash', self.pos_profile, self.from_date, self.to_date, self.name)

		# Fetch existing POS Closing entries from the child table to avoid duplication
		existing_entries = [d.pos_closing_entry for d in self.items]

		for d in frappe.db.sql(query, params, as_dict=True):
			if d['pos_closing_entry'] not in existing_entries:
				row = self.append('items', {})
				row.update(d)
