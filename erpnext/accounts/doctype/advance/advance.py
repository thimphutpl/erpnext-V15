import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import money_in_words
from erpnext.custom_utils import prepare_gl
from frappe.utils import flt,nowtime

class Advance(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.advance_item.advance_item import AdvanceItem
		from frappe.types import DF

		advance_details: DF.Table[AdvanceItem]
		advance_type: DF.Link
		amended_from: DF.Link | None
		branch: DF.Link
		company: DF.Link
		cost_center: DF.Link | None
		customer: DF.DynamicLink | None
		customer_cid: DF.Data | None
		employee: DF.Link | None
		employee_name: DF.Data | None
		fiscal_year: DF.Link | None
		is_opening: DF.Check
		journal_entry: DF.Link | None
		mode_of_payment: DF.Link | None
		party_type: DF.Literal["", "Supplier", "Employee", "Customer"]
		posting_date: DF.Date | None
		remarks: DF.SmallText | None
		total_amount: DF.Currency
	# end: auto-generated types

	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link | None
		advance_amount: DF.Float
		advance_type: DF.Link
		amended_from: DF.Link | None
		branch: DF.Link | None
		budget_activity: DF.Link
		budget_sub_activity: DF.Link
		company: DF.Link
		cost_center: DF.Link | None
		customer: DF.DynamicLink
		customer_cid: DF.Data | None
		employee: DF.Link | None
		employee_name: DF.Data | None
		is_opening: DF.Check
		item_code: DF.Data | None
		item_name: DF.Data | None
		opening_balance: DF.Float
		party_type: DF.Literal["", "Customer", "Supplier", "Employee"]
		posting_date: DF.Date | None
		remarks: DF.SmallText | None
		source_of_fund: DF.Link
	def validate(self):
		# self.calcalute_tds()
		# self.calculate_retention()
		self.calculate_total_amount()




	def on_submit(self):
		self.post_journal_entry()
		self.make_mobilisation_entry()

	def cancel(self):
		self.ignore_linked_doctypes = (
			"Journal Entry",
			"GL Entry",
			"Payment Ledger Entry",
		)

		return super().cancel()


	def on_cancel(self):
		self.cancel_linked_advance_entry()




	def cancel_linked_advance_entry(self):
		advance_entries = frappe.get_all(
			"Advance Entry",
			filters={
				"advance": self.name,
				"docstatus": 1
			},
			pluck="name"
		)

		for advance_entry in advance_entries:
			doc = frappe.get_doc("Mobilisation Entry Item", advance_entry)
			doc.cancel()


	# def cancel_general_ledger(self):
	# 	frappe.db.sql("""
	# 		UPDATE `tabGL Entry`
	# 		SET is_cancelled = 1
	# 		where voucher_no = %s
	# 		AND is_cancelled = 0
	# 	""", (self.name,))

		frappe.db.commit()


	def calculate_total_amount(self):
		total_amount = 0

		for item in self.advance_details:
			total_amount += item.opening_balance or 0

		self.total_amount = total_amount

	
	

	def post_journal_entry(self):
		debit_account = frappe.db.get_value("Advance Type", self.advance_type, "advance_account")
		credit_account = None
		voucher_type = ""
		voucher_series = ""
		party_type = ""
		party = ""
		account_type=""
		if self.is_opening == 1:
			credit_account = frappe.db.get_value(
				"Company", self.company, "default_temporary_account"
			)
	
		elif self.mode_of_payment == "Cash":
			credit_account = frappe.db.get_value(
				"Company", self.company, "default_cash_account"
			)
		elif self.mode_of_payment == "Wire Transfer":
			credit_account = frappe.db.get_value(
				"Company", self.company, "default_bank_account"
			)

		else:
			credit_account = frappe.db.get_value(
				"Company", self.company, "default_bank_account"
			)
	
	
		if not debit_account:
			frappe.throw("Setup Default Advance Account in Advance Type <b>{}</b>".format(self.advance_type))

		if not credit_account:
			frappe.throw("Setup Default Bank Account in Company Settings")

		

		debit_account_type = frappe.db.get_value("Account", debit_account, "account_type")

		for item in self.advance_details:
			account = item.tds_account

			account_type = frappe.db.get_value(
				"Account", account, "account_type"
			)
		for item in self.advance_details:
			account = item.retention_account

			account_type = frappe.db.get_value(
				"Account", account, "account_type"
			)



		if self.is_opening:
			voucher_type = "Opening Entry"
			voucher_series = "Opening Entry"
		else:
			voucher_type = "Disbursement Voucher"
			voucher_series = "Disbursement Voucher"
		naming_series = frappe.db.get_value(
			"Journal Entry Series",
			voucher_series,
			"name"
		)

		if debit_account_type in ("Payable", "Receivable") or account_type in ("Payable", "Receivable"):
			party_type = self.party_type
			party = self.customer
		elif debit_account_type == "Expense Account":
			party_type = ""
			party = ""
		remarks = []
		if self.remarks:
			remarks.append(_("Note: {0}").format(self.remarks))

		remarkss = "".join(remarks)
		je = frappe.new_doc("Journal Entry")
		je.voucher_type = voucher_type
		je.naming_series = naming_series
		je.title = "Advance - " + self.name
		je.remark = remarkss if remarkss else "Note: " + "Advance - " + self.name
		je.posting_date = self.posting_date
		je.company = self.company
		je.total_amount_in_words = money_in_words(self.total_amount)
		je.branch = self.branch
		je.reference_doctype= self.doctype
		je.reference_link = self.name
		je.mode_of_payment=self.mode_of_payment
		if flt(self.total_amount) > 0:
	  
			je.append("accounts", {
				"account": credit_account,
				"reference_type": "Advance",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": self.total_amount,
				"credit": self.total_amount,
			})

		for item in self.advance_details:
			amount = flt(item.amount)
			tds_amount = flt(item.tds_amount)
			retention_amount = flt(item.retention_amount)
			if amount:
				je.append("accounts", {
					"account": debit_account,
					"reference_type": "Advance",
					"reference_name": self.name,
					"cost_center": self.cost_center,
					"debit_in_account_currency": flt(amount),
					"debit": flt(amount),
					"party_type": party_type,
					"party": party

				})

			# TDS
			if tds_amount > 0 and item.tds_account:
				je.append("accounts", {
					"account": item.tds_account,
					"reference_type": "Advance",
					"reference_name": self.name,
					"cost_center": self.cost_center,
					"debit_in_account_currency": tds_amount,
					"credit": tds_amount,
					"party_type": party_type,
					"party": party
				})

			# RETENTION
			if retention_amount > 0 and item.retention_account:
				je.append("accounts", {
					"account": item.retention_account,
					"reference_type": "Advance",
					"reference_name": self.name,
					"cost_center": self.cost_center,
					"debit_in_account_currency": retention_amount,
					"debit": retention_amount,
					"party_type": party_type,
					"party": party
				})



	
		je.insert()
		self.db_set("journal_entry", je.name)
		frappe.msgprint("Journal Entry created. {}".format(frappe.get_desk_link("Journal Entry", je.name)))

	def make_mobilisation_entry(self, cancel=False):
		party = None
		if  self.party_type == "Customer":
			party = self.customer
		elif self.party_type == "Supplier":
			party = self.customer
		else:
			party = self.customer
		account = frappe.db.get_value("Advance Type", self.advance_type, "advance_account")

		con = frappe.new_doc("Advance Entry")
		con.branch = self.branch
		con.posting_date = self.posting_date
		con.posting_time = nowtime()
		con.party_type= self.party_type
		con.customer = party
		con.advance_type=self.advance_type
		con.branch = self.branch
		con.reference_type = "Advance Entry"
		con.is_running_bill = 0
		con.is_opening=self.is_opening
		con.advance = self.name
  
		for item in self.advance_details:
			net_amount = (
				(item.amount or 0)
			)
			budget_activity = item.budget_activity
			budget_sub_activity = item.budget_sub_activity
			source_of_fund = item.source_of_fund
   
			con.append("mobilisation_entry", {
				"reference":self.name,
				"advance_type":self.advance_type,
				"total_amount": net_amount,
				"budget_activity": budget_activity,
				"budget_sub_activity":budget_sub_activity,
				"source_of_fund":source_of_fund,   
				"account": account,
				"advance_amount": net_amount,
				"balance_amount": net_amount
			})
		con.insert(ignore_permissions=True)
		con.submit()


@frappe.whitelist()
def tax_account(name,company):
	doc = frappe.db.sql("""
		SELECT
			twr.tax_withholding_rate,
			twa.account
		FROM `tabTax Withholding Category` AS twc
		INNER JOIN `tabTax Withholding Rate` AS twr
			ON twc.name = twr.parent
		INNER JOIN `tabTax Withholding Account` AS twa
			ON twc.name = twa.parent
		WHERE
			twc.name = %s
		AND
			twa.company = %s
	""", (name,company), as_dict=True)

	return doc[0] if doc else None


def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles or "Accounts User" in user_roles or "Accounts Manager" in user_roles:
		return

	return """(
		exists(select 1
			from `tabEmployee` as e
			where e.branch = `tabAdvance`.branch
			and e.user_id = '{user}')
	)""".format(user=user)