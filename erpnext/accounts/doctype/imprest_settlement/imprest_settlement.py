# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _, scrub
from frappe.model.document import Document


class ImprestSettlement(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.model.document import Document
		from frappe.types import DF

		from erpnext.accounts.doctype.imprest_advance_item.imprest_advance_item import ImprestAdvanceItem

		advances: DF.Table[ImprestAdvanceItem]
		amended_from: DF.Link | None
		branch: DF.Link
		company: DF.Link
		cost_center: DF.Link | None
		items: DF.Table[Document]
		journal_entry: DF.Data | None
		party: DF.DynamicLink
		party_type: DF.Literal["", "Employee", "Agency"]
		posting_date: DF.Date
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
		self.post_journal_entry()

	def on_cancel(self):
		self.update_advance_ref_doc(cancel=True)
		self.update_outstanding_amount(cancel=True)


	def calculate_amount(self):
		total_allocated = sum(d.allocated_amount for d in self.items) if self.items else 0
		self.total_allocated_amount = total_allocated

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
			else:
				doc.balance_amount -= ref.allocated_amount
				doc.adjusted_amount += ref.allocated_amount
			doc.save()

	def update_outstanding_amount(self, cancel=False):
		for item in self.get("items"):
			doc = frappe.get_doc(item.reference_doctype, item.reference_name)
			if cancel:
				doc.outstanding_amount += item.allocated_amount
			else:
				doc.outstanding_amount -= item.allocated_amount
			doc.save()

	def post_journal_entry(self):
		imprest_advance_account = frappe.db.get_value("Company", self.company, "imprest_advance_account")
		bank_account = frappe.db.get_value("Company", self.company, "default_bank_account")
		if not bank_account:
			frappe.throw(f"Set default bank account in company {frappe.bold(self.company)}")
		if not imprest_advance_account:
			frappe.throw("Set Imprest Advance Account in {}".format(
				frappe.get_desk_link("Company", self.company)
			))
		accounts = []
		accounts.append({
			"account": bank_account,
			"cost_center": self.cost_center,
			"debit": self.total_allocated_amount,
			"debit_in_account_currency": self.total_allocated_amount,
			"reference_type": self.doctype,
			"reference_name": self.name
		})
		accounts.append({
			"account": imprest_advance_account,
			"cost_center": self.cost_center,
			"party_type": self.party_type,
			"party": self.party,
			"credit": self.total_allocated_amount,
			"credit_in_account_currency": self.total_allocated_amount,
			"reference_type": self.doctype,
			"reference_name": self.name
		})

		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permission = 1
		je.update({
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"naming_series": "Journal Voucher",
			"posting_date": self.posting_date,
			"company": self.company,
			"branch": self.branch,
			# "reference_doctype": self.doctype,
			# "reference_name": self.name,
			"accounts": accounts,
		})
		je.submit()
		self.db_set('journal_entry', je.name)
		frappe.msgprint(_('Journal Entry {0} posted').format(frappe.get_desk_link("Journal Entry", je.name)))

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
							posting_date, conversion_rate as exchange_rate
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
