# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _, scrub
from frappe.model.document import Document
from frappe.utils import flt
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController

class ImprestSettlement(AccountsController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.imprest_advance_item.imprest_advance_item import ImprestAdvanceItem
		from erpnext.accounts.doctype.imprest_settlement_item.imprest_settlement_item import ImprestSettlementItem
		from erpnext.accounts.doctype.imprest_settlement_reference.imprest_settlement_reference import ImprestSettlementReference
		from frappe.types import DF

		advances: DF.Table[ImprestAdvanceItem]
		amended_from: DF.Link | None
		branch: DF.Link
		company: DF.Link
		cost_center: DF.Link | None
		items: DF.Table[ImprestSettlementItem]
		journal_entry: DF.Data | None
		party: DF.DynamicLink
		party_type: DF.Literal["", "Employee", "Agency"]
		posting_date: DF.Date
		references: DF.Table[ImprestSettlementReference]
		remarks: DF.SmallText | None
		total_advance_amount: DF.Currency
		total_allocated_amount: DF.Currency
	# end: auto-generated types

	def validate(self):
		self.calculate_amount()
		self.populate_imprest_advance()
		self.calculate_total_advance()
		self.validate_data()

	def on_submit(self):
		self.update_advance_ref_doc()
		self.update_outstanding_amount()
		self.make_gl_entries()

	def on_cancel(self):
		self.update_advance_ref_doc(cancel=True)
		self.update_outstanding_amount(cancel=True)
		self.make_gl_entries(cancel=True)

	def calculate_amount(self):
		total_allocated_ref = sum(d.allocated_amount for d in self.references) if self.references else 0
		total_allocated_item = sum(d.amount for d in self.items) if self.items else 0
		self.total_allocated_amount = flt(total_allocated_ref) + flt(total_allocated_item)

	def calculate_total_advance(self):
		total_advance = 0
		for adv in self.get('advances'):
			total_advance += adv.advance_amount
		self.total_advance_amount = total_advance

	def validate_data(self):
		if self.total_allocated_amount > self.total_advance_amount:
			frappe.throw(f"Total Allocated Amount {frappe.bold(self.total_allocated_amount)} cannot be greater than total advance amount {frappe.bold(self.total_advance_amount)}")

	def update_advance_ref_doc(self, cancel=False):
		for ref in self.advances:
			doc = frappe.get_doc("Imprest Advance", ref.imprest_advance)
			if cancel:
				doc.balance_amount += ref.allocated_amount
				doc.adjusted_amount -= ref.allocated_amount
				doc.payment_status = "Unpaid"
			else:
				doc.balance_amount -= ref.allocated_amount
				doc.adjusted_amount += ref.allocated_amount
				doc.payment_status = "Paid"
			doc.save()

	def update_outstanding_amount(self, cancel=False):
		for item in self.get("references"):
			doc = frappe.get_doc(item.reference_doctype, item.reference_name)
			if cancel:
				doc.outstanding_amount += item.allocated_amount
			else:
				doc.outstanding_amount -= item.allocated_amount
			doc.save()

	def make_gl_entries(self, cancel=False):
		gl_entries = []
		for item in self.items:
			gl_entries.append(
				self.get_gl_dict({
					"account": item.account,
					"debit": item.amount,
					"debit_in_account_currency": item.amount,
					"voucher_type": self.doctype,
					"voucher_no": self.name,
					"cost_center": self.cost_center,
					"party_type": self.party_type,
					"party": self.party,
					# "business_activity": item.business_activity,
					# "against_voucher_type":	item.invoice_type,
					# "against_voucher": item.invoice_no
			}))

		for ref in self.references:
			gl_entries.append(
				self.get_gl_dict({
					"account": ref.account,
					"debit": ref.allocated_amount,
					"debit_in_account_currency": ref.allocated_amount,
					"voucher_type": self.doctype,
					"voucher_no": self.name,
					"cost_center": self.cost_center,
					"party_type": self.party_type,
					"party": self.party,
					# "business_activity": item.business_activity,
					"against_voucher_type":	ref.reference_doctype,
					"against_voucher": ref.reference_name
			}))

		credit_account = frappe.db.get_value("Company", self.company, "imprest_advance_account")
		if not credit_account:
			frappe.throw("Set Imprest Advance Account in {}".format(
				frappe.get_desk_link("Company", self.company)
			))
		gl_entries.append(
			self.get_gl_dict({
				"account": credit_account,
				"credit": self.total_allocated_amount,
				"credit_in_account_currency": self.total_allocated_amount,
				"party_type": self.party_type,
				"party": self.party,
				"voucher_type": self.doctype,
				"voucher_no": self.name,
				"cost_center": self.cost_center,
			}))
		make_gl_entries(gl_entries, cancel, update_outstanding="No", merge_entries=False)

	# def post_journal_entry(self):
	# 	imprest_advance_account = frappe.db.get_value("Company", self.company, "imprest_advance_account")
	# 	bank_account = frappe.db.get_value("Company", self.company, "default_bank_account")
	# 	if not bank_account:
	# 		frappe.throw(f"Set default bank account in company {frappe.bold(self.company)}")
	# 	if not imprest_advance_account:
	# 		frappe.throw("Set Imprest Advance Account in {}".format(
	# 			frappe.get_desk_link("Company", self.company)
	# 		))
	# 	accounts = []
	# 	accounts.append({
	# 		"account": bank_account,
	# 		"cost_center": self.cost_center,
	# 		"debit": self.total_allocated_amount,
	# 		"debit_in_account_currency": self.total_allocated_amount,
	# 		"reference_type": self.doctype,
	# 		"reference_name": self.name
	# 	})
	# 	accounts.append({
	# 		"account": imprest_advance_account,
	# 		"cost_center": self.cost_center,
	# 		"party_type": self.party_type,
	# 		"party": self.party,
	# 		"credit": self.total_allocated_amount,
	# 		"credit_in_account_currency": self.total_allocated_amount,
	# 		"reference_type": self.doctype,
	# 		"reference_name": self.name
	# 	})

	# 	je = frappe.new_doc("Journal Entry")
	# 	je.flags.ignore_permission = 1
	# 	je.update({
	# 		"doctype": "Journal Entry",
	# 		"voucher_type": "Journal Entry",
	# 		"naming_series": "Journal Voucher",
	# 		"posting_date": self.posting_date,
	# 		"company": self.company,
	# 		"branch": self.branch,
	# 		# "reference_doctype": self.doctype,
	# 		# "reference_name": self.name,
	# 		"accounts": accounts,
	# 	})
	# 	je.submit()
	# 	self.db_set('journal_entry', je.name)
	# 	frappe.msgprint(_('Journal Entry {0} posted').format(frappe.get_desk_link("Journal Entry", je.name)))

	@frappe.whitelist()
	def populate_imprest_advance(self):
		if not self.party or not self.branch:
			frappe.throw("Please insert the mandatory fields")
		else:
			self.set('advances', [])
			query = f"""
				SELECT
					a.name, a.opening_amount, a.advance_amount, a.balance_amount, a.is_opening
				FROM `tabImprest Advance` a
				WHERE a.docstatus = 1
					AND a.posting_date <= '{self.posting_date}'
					AND a.balance_amount > 0
					AND a.party = '{self.party}'
				ORDER BY a.posting_date
			"""

			data = frappe.db.sql(query, as_dict=True)

			if not data:
				frappe.throw("No Imprest Advance")

			allocated_amount = self.total_allocated_amount or 0

			for d in data:
				row = self.append('advances', {
					'imprest_advance': d.name,
					'advance_amount': d.balance_amount,
				})

				if d.balance_amount >= allocated_amount:
					row.allocated_amount = allocated_amount
					row.balance_amount = d.balance_amount - allocated_amount
					allocated_amount = 0
				else:
					row.allocated_amount = d.balance_amount
					row.balance_amount = 0
					allocated_amount -= d.balance_amount

			if not self.advances:
				frappe.throw("No Imprest Advance")

@frappe.whitelist()
def get_outstanding_reference_documents(args):
	if isinstance(args, str):
		args = json.loads(args)

	company_currency = frappe.get_cached_value("Company", args.get("company"), "default_currency")

	outstanding_invoices = get_outstanding_invoices(
     												args.get('party_type'),
                 									args.get('party'),
													company_currency,
													args.get('company')
                          						)

	data = outstanding_invoices

	if not data:
		frappe.msgprint(
			_(
				"No outstanding invoices found for the {0} {1} which qualify the filters you have specified."
			).format(_(args.get("party_type")).lower(), frappe.bold(args.get("party")))
		)

	return data

def get_outstanding_invoices(party_type, party, company_currency, company):
    voucher_type = "Purchase Invoice"
    return frappe.db.sql("""
                        select
							'{voucher_type}' as voucher_type,
       						name as voucher_no,
							case when currency = '{company_currency}' then grand_total else base_grand_total end as invoice_amount,
							outstanding_amount,
							posting_date, conversion_rate as exchange_rate,
							credit_to as account
						from
      						`tab{voucher_type}`
						where
							{party_type} = %s
       						and docstatus = 1
							and outstanding_amount > 0
							and company =%s
						order by
							posting_date, name
                         """.format(
                            **{
								"voucher_type": voucher_type,
								"company_currency": company_currency,
								"party_type": scrub(party_type),
						 	}
                        ),(party, company), as_dict=True)
