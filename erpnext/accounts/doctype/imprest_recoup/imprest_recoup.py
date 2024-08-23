# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt, cint, nowdate, getdate, formatdate, money_in_words
# from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states

class ImprestRecoup(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.imprest_advance_item.imprest_advance_item import ImprestAdvanceItem
		from erpnext.accounts.doctype.imprest_recoup_item.imprest_recoup_item import ImprestRecoupItem
		from erpnext.accounts.doctype.transaction_selection.transaction_selection import TransactionSelection
		from frappe.types import DF

		abstract_bill: DF.Data | None
		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Link | None
		approver_name: DF.Data | None
		balance_amount: DF.Currency
		branch: DF.Link
		business_activity: DF.Link
		company: DF.Link
		cost_center: DF.Link
		excess_amount: DF.Currency
		fetch_from_other_transactions: DF.Check
		final_je: DF.Data | None
		final_settlement: DF.Literal["", "Yes", "No"]
		imprest_advance_list: DF.Table[ImprestAdvanceItem]
		imprest_type: DF.Link
		items: DF.Table[ImprestRecoupItem]
		journal_entry: DF.Data | None
		opening_balance: DF.Currency
		party: DF.DynamicLink
		party_type: DF.Literal["", "Employee", "Agency"]
		posting_date: DF.Date
		remarks: DF.SmallText | None
		select_transactions: DF.TableMultiSelect[TransactionSelection]
		title: DF.Data
		total_allocated_amount: DF.Currency
		total_amount: DF.Currency
	# end: auto-generated types

	def validate(self):
		self.calculate_amount()
		self.populate_imprest_advance()
		self.set_recoup_account(validate=True)
		self.calculate_amount_final()
	
	def set_recoup_account(self, validate=False):
		for d in self.items:
			if not d.account or not validate:
				d.account = get_imprest_recoup_account(d.recoup_type, self.company)[
					"account"
				]

	def calculate_amount(self):
		total_payable_amt = sum(d.amount for d in self.items) if self.items else 0
		self.total_amount = total_payable_amt
	
	def calculate_amount_final(self):
		tot_adv_amt = sum(d.advance_amount for d in self.imprest_advance_list)
		tot_bal_amt = sum(d.balance_amount for d in self.imprest_advance_list)
		tot_allocated_amt = sum(d.allocated_amount for d in self.imprest_advance_list)
		self.opening_balance = flt(tot_adv_amt)
		self.balance_amount = flt(tot_bal_amt)
		self.total_allocated_amount = flt(tot_allocated_amt)
		if flt(self.total_amount) > flt(tot_allocated_amt):
			self.excess_amount = flt(self.total_amount) - flt(tot_allocated_amt)
		else:
			self.excess_amount = 0
		
		# if self.docstatus != 1 and tot_bal_amt <= 0:
		# 	frappe.throw("Expense amount cannot be more than balance amount.")

	def on_submit(self):
		self.update_reference_document()
		if self.final_settlement == "Yes":
			self.create_abstract_bill()
		else:
			self.create_abstract_bill()
			self.create_auto_imprest_advance()		

	def create_abstract_bill(self):
		bank_account = frappe.db.get_value("Company", self.company, "default_bank_account")
		if not bank_account:
			frappe.throw("Set Default Bank Account in Company {}".format(frappe.get_desk_link(self.company)))
		items = []
		for item in self.get("items"):
			items.append({
				"account": item.account,
				"cost_center": item.cost_center,
				"party_type": self.party_type,
				"party": self.party,
				"business_activity": item.business_activity,
				"amount": item.amount,
				"cash_receipt": self.balance_amount if self.final_settlement == "Yes" else 0,
				"reimburse_amount": self.excess_amount if self.final_settlement == "Yes" else 0
			})
		if self.balance_amount and self.final_settlement == "Yes":
			items.append({
				"account": bank_account,
				"cost_center": self.cost_center,
				"party_type": self.party_type,
				"party": self.party,
				"business_activity": self.business_activity,
				"amount": self.balance_amount,
				"not_required": 1,
			})
		ab = frappe.new_doc("Abstract Bill")
		ab.flags.ignore_permission = 1
		ab.update({
			"doctype": "Abstract Bill",
			"posting_date": self.posting_date,
			"branch": self.branch,
			"company": self.company,
			"reference_doctype": self.doctype,
			"reference_name": self.name,
			"items": items,
			"final_settlement": 1 if self.final_settlement == "Yes" else 0
		})
		ab.insert()
		self.db_set('abstract_bill', ab.name)
		frappe.msgprint(_('Abstract Bill {0} created').format(frappe.get_desk_link("Abstract Bill", ab.name)))
	
	def before_cancel(self):
		if self.abstract_bill:
			ab_status = frappe.get_value("Abstract Bill", {"name": self.abstract_bill}, "docstatus")
			if cint(ab_status) == 1:
				frappe.throw("Abstract Bill {} for this transaction needs to be cancelled first".format(frappe.get_desk_link("Abstract Bill", self.abstract_bill)))
			else:
				frappe.db.sql("delete from `tabAbstract Bill` where name = '{}'".format(self.abstract_bill))
				self.db_set("abstract_bill", None)

		self.check_imprest_advance_status_and_cancel()
		
	def on_cancel(self):
		self.update_reference_document(cancel=True)
		self.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry")

	def check_imprest_advance_status_and_cancel(self):
		ima = frappe.db.sql("select name from `tabImprest Advance` where imprest_recoup = '{}' and docstatus = 1".format(self.name))
		if ima:
			ia_doc = frappe.get_doc("Imprest Advance", {"name": ima})
			ia_doc.cancel()

	def post_refund_je(self):
		bank_account = frappe.db.get_value("Company", self.company, "default_bank_account")
		if not bank_account:
			frappe.throw("Set Default Bank Account in Company {}".format(frappe.get_desk_link(self.company)))
		credit_account = frappe.db.get_value("Company", self.company, "default_cash_account")
		if not credit_account:
			frappe.throw("Set Default Cash Account in Company {}".format(frappe.get_desk_link(self.company)))
		
		# Posting Journal Entry
		je = frappe.new_doc("Journal Entry")
		je.update({
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"naming_series": "ACC-JV-.YYYY.-",
			"title": f"Refund Imprest advance for - {self.party}",
			"posting_date": self.posting_date,
			"company": self.company,
			"branch": self.branch
		})

		je.append("accounts", {
			"account": bank_account,
			"debit_in_account_currency": flt(self.balance_amount),
			"cost_center": self.cost_center,
		})
		
		je.append("accounts", {
			"account": credit_account,
			"credit_in_account_currency": flt(self.balance_amount),
			"cost_center": self.cost_center,
			"reference_type": "Imprest Recoup",
			"reference_name": self.name,
			"party_type": self.party_type,
			"party": self.party,
		})
		je.insert()
		frappe.msgprint("Journal Entry created. {}".format(frappe.get_desk_link("Journal Entry", je.name)))
	
	@frappe.whitelist()
	def populate_imprest_advance(self):
		if not self.imprest_type or not self.party or not self.branch:
			frappe.throw("Please insert the mandatory fields")
		else:
			self.set('imprest_advance_list', [])
			query = """
				SELECT 
					a.name, a.opening_amount, a.advance_amount, a.balance_amount, a.is_opening
				FROM `tabImprest Advance` a
				WHERE a.docstatus = 1 
					AND a.posting_date <= '{date}'
					AND a.balance_amount > 0
					AND a.imprest_type = '{imprest_type}'
					AND a.party = '{party}'
				ORDER BY a.posting_date
			""".format(date=self.posting_date, imprest_type=self.imprest_type, party=self.party)

			data = frappe.db.sql(query, as_dict=True)

			if not data:
				frappe.throw("No Imprest Advance")

			allocated_amount = self.total_amount or 0
			total_amount_adjusted = 0

			for d in data:
				row = self.append('imprest_advance_list', {
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

			if not self.imprest_advance_list:
				frappe.throw("No Imprest Advance")

	def update_reference_document(self, cancel=False):
		for d in self.imprest_advance_list:
			doc = frappe.get_doc("Imprest Advance", d.imprest_advance)
			allocated_amount = flt(d.allocated_amount)
			if cancel:
				doc.balance_amount += allocated_amount
				doc.adjusted_amount -= allocated_amount
			else:
				doc.balance_amount -= allocated_amount
				doc.adjusted_amount += allocated_amount
			doc.save(ignore_permissions=True)

	def create_auto_imprest_advance(self):
		imprest_limit = frappe.db.get_value("Imprest Type",  self.imprest_type, "imprest_max_limit")
		if not imprest_limit:
			frappe.throw("Please set Imprest Limit in {}".format(
				frappe.get_desk_link("Imprest Type", self.imprest_type)
			))

		bal_amt = flt(imprest_limit) - flt(self.total_allocated_amount)
		if bal_amt > 0:
			advance_amount = flt(bal_amt)
		else:
			advance_amount = flt(imprest_limit)
			
		if self.total_amount:
			ima = frappe.new_doc("Imprest Advance")
			ima.update({
				"branch": self.branch,
				"posting_date": self.posting_date,
				"title": f"Auto Imprest Allocation from - {self.name}",
				"remarks": f"Note: Auto created Imprest Advance Allocation from Recoup - {self.name}",
				"company": self.company,
				"imprest_type": self.imprest_type,
				"party_type": self.party_type,
				"party": self.party,
				"advance_amount": advance_amount,
				"imprest_recoup": self.name,
				"balance_amount": advance_amount,
				"business_activity": self.business_activity,
			})
			ima.insert()
			ima.submit()
			frappe.msgprint("Imprest Advance created. {}".format(frappe.get_desk_link("Imprest Advance", ima.name)))

	@frappe.whitelist()
	def get_transactions_detail(self):
		# if self.transaction_type == "Purchase Invoice":
		if not self.party:
			frappe.throw("Select the party to retrieve transactions associated with them.")
		transaction=[]
		for i in self.select_transactions:
			transaction.append(i.transaction_name)
		#frappe.throw(str(transaction))
		data1, data2, data3= [],[],[]
		if 'Repair And Services' in transaction:
			
			data1 = frappe.db.sql('''
								SELECT 
									rs.name AS reference_name,
									rs.cash_memo_number AS invoice_no,
									rs.invoice_date,
									rs.cost_center,
									rs.total_amount AS amount,
									rs.business_activity
								FROM 
									`tabRepair And Services` rs
								LEFT JOIN 
									`tabImprest Recoup Item` iri 
								ON 
									rs.name = iri.reference_name
								WHERE 
									rs.imprest_party = {party}
									and rs.settle_from_advance = 1
									AND (iri.reference_name IS NULL OR iri.docstatus = 2);

							'''.format(party=self.party),as_dict=True)

			for d in data1:
				d['reference_type'] = 'Repair And Services'
			
		if 'Insurance and Registration' in transaction:
			
			data2 = frappe.db.sql('''
								SELECT 
									ir.name AS reference_name,
									ir.cost_center as cost_center,
									ir.total_amount AS amount
								FROM 
									`tabInsurance and Registration` ir
								LEFT JOIN 
									`tabImprest Recoup Item` iri 
								ON 
									ir.name = iri.reference_name
								WHERE 
									ir.imprest_party = {party}
									and ir.settle_from_advance = 1
									AND (iri.reference_name IS NULL OR iri.docstatus = 2);


							'''.format(party=self.party),as_dict=True)
			for d in data2:
				d['reference_type'] = 'Insurance and Registration'
    
		if 'Purchase Invoice' in transaction:
			
			data3 = frappe.db.sql('''
								SELECT 
						pii.item_code, 
						pii.sub_ledger AS account,                         
						pi.name AS reference_name,
						pii.base_amount AS amount,                         
						pii.business_activity AS business_activity,                         
						pi.supplier_name AS party,
						pii.cost_center
						FROM 
							`tabPurchase Invoice Item` pii 
						INNER JOIN 
							`tabPurchase Invoice` pi 
							ON pi.name = pii.parent
						LEFT JOIN 
							`tabImprest Recoup Item` iri 
							ON pi.name = iri.reference_name
						WHERE 
							pi.settle_from_advance = 1
							and (iri.reference_name IS NULL OR iri.docstatus = 2)
       						and pi.imprest_party = {imprest_party};


							'''.format(imprest_party=self.party),as_dict=True)
			for d in data3:
				d['reference_type'] = 'Purchase Invoice'
    
		data = data1 + data2 + data3

		self.set('items',[])
			
		if not data:
			frappe.throw(_("No Transactions Found"))

		for d in data:
			# d['party_type'] = 'Supplier'
			# d['reference_type'] = 'Repair And Services'
			self.append('items', d)

		return True
 
	
@frappe.whitelist()
def get_imprest_recoup_account(recoup_type, company):
	account = frappe.db.get_value(
		"Imprest Recoup Account", {"parent": recoup_type, "company": company}, "default_account"
	)
	if not account:
		frappe.throw(
			_("Set the default account for the {0} {1}").format(
				frappe.bold("Recoup Type"), get_link_to_form("Recoup Type", recoup_type)
			)
		)
	return {"account": account}


def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles or "Accounts User" in user_roles or "Account Manager" in user_roles: 
		return

	return """(
		`tabImprest Recoup`.owner = '{user}'
		or
		exists(select 1
			from `tabEmployee` as e
			where e.branch = `tabImprest Recoup`.branch
			and e.user_id = '{user}')
		or
		exists(select 1
			from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
			where e.user_id = '{user}'
			and ab.employee = e.name
			and bi.parent = ab.name
			and bi.branch = `tabImprest Recoup`.branch)
	)""".format(user=user)