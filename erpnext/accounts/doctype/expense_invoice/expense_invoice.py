# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate, get_datetime, get_url, nowdate, now_datetime, money_in_words
from erpnext.custom_utils import check_future_date

class ExpenseInvoice(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.epayment.doctype.utility_bill_item.utility_bill_item import UtilityBillItem
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		business_activity: DF.Link
		cost_center: DF.Link
		direct_payment: DF.Link | None
		employee: DF.Link
		is_rental: DF.Check
		item: DF.Table[UtilityBillItem]
		net_payable_amount: DF.Currency
		party: DF.Data | None
		posting_date: DF.Date
		remark: DF.SmallText | None
		tds_account: DF.Link | None
		tds_percent: DF.Literal["", "2", "3", "5", "10"]
		title: DF.Data
		total_bill_amount: DF.Currency
		total_tds_amount: DF.Currency
		workflow_state: DF.Link | None
	# end: auto-generated types
	def validate(self):
		check_future_date(self.posting_date)
		self.calculate_amt()

	def on_submit(self):
		self.validate_rental()
		self.make_direct_payment()
	   

	def calculate_amt(self):
		total_inv_amount = total_tds_amount = total_net_amount = 0.00
		party=None
		for a in self.item:
			net_amount = tds_amount = 0.00
			if a.tds_applicable:
				if a.invoice_amount > 0:
					if cint(self.tds_percent) > 0:
						tds_amount = flt(a.invoice_amount) * flt(self.tds_percent)/100

			net_amount = flt(a.invoice_amount) - flt(tds_amount)
			a.tds_amount = tds_amount
			a.net_amount = net_amount
			total_inv_amount += flt(a.invoice_amount)
			total_tds_amount += flt(a.tds_amount)
			total_net_amount += flt(a.net_amount)
			party=a.party

		self.total_bill_amount  = total_inv_amount
		self.total_tds_amount   = total_tds_amount
		self.net_payable_amount = total_net_amount
		self.party= party
	
	def validate_rental(self):
		if self.is_rental:
			for a in self.item:
				for a in frappe.db.sql("""
						select u.name as util_payment from
						`tabUtility Bill` u inner join `tabUtility Bill Item` i
						on u.name = i.parent
						where u.docstatus = 1
						and i.party = '{0}'
						and u.year = '{1}'
						and u.month = '{2}' and u.name != '{3}'
					  """.format(a.party, self.year, self.month, self.name), as_dict=True):
					if a.util_payment:
						frappe.throw("Rental payment done for party {} in Utility Bill No. {}".format(a.party, a.util_payment))
	@frappe.whitelist()
	def make_direct_payment(self):
		
		doc = frappe.new_doc("Direct Payment")
		doc.branch = self.branch
		doc.cost_center = self.cost_center
		doc.posting_date = self.posting_date
		doc.payment_type = "Payment"
		doc.business_activity = self.business_activity
		doc.tds_percent = self.tds_percent
		doc.tds_account = self.tds_account
		doc.remarks = self.remark
		for a in self.item:
			doc.append("item", {
				"party_type": "Supplier",
				"party": a.party,
				"account": a.debit_account,
				"amount": a.invoice_amount,
				"invoice_no": a.invoice_no,
				"invoice_date": a.invoice_date,
				"tds_applicable": a.tds_applicable,
				"taxable_amount": a.invoice_amount,
				"tds_amount": a.tds_amount,
				"net_amount": a.net_amount,
			})
		doc.save()
		self.db_set("direct_payment", doc.name)
		frappe.msgprint(_('Successfully posted to accounts'))
		frappe.db.commit()
		
def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles: 
		return

	return """(
		exists(select 1
			from `tabEmployee` as e
			where e.branch = `tabExpense Invoice`.branch
			and e.user_id = '{user}')
		or
		exists(select 1
			from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
			where e.user_id = '{user}'
			and ab.employee = e.name
			and bi.parent = ab.name
			and bi.branch = `tabExpense Invoice`.branch)
	)""".format(user=user)
