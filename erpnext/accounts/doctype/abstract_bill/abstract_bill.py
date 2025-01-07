# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import (
	cint,
	cstr,
	flt,
	formatdate,
	get_link_to_form,
	getdate,
	now_datetime,
	nowtime,
	strip,
	strip_html,
)


class AbstractBill(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from erpnext.accounts.doctype.abstract_bill_item.abstract_bill_item import AbstractBillItem

		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_name: DF.Data | None
		base_total_amount: DF.Currency
		branch: DF.Link
		company: DF.Link
		cost_center: DF.Link
		currency: DF.Link | None
		dispatch_number: DF.Data | None
		exchange_rate: DF.Float
		fetch_other_transactions: DF.Check
		file_index: DF.Link | None
		final_settlement: DF.Check
		fiscal_year: DF.Link | None
		items: DF.Table[AbstractBillItem]
		journal_entry: DF.Data | None
		journal_entry_status: DF.Data | None
		mode_of_payment: DF.Literal["", "Bank Entry", "Cash Entry"]
		posting_date: DF.Date
		reference: DF.SmallText | None
		reference_doctype: DF.Link | None
		reference_name: DF.DynamicLink | None
		total_amount: DF.Currency
		transaction_type: DF.Literal["", "Purchase Invoice"]
	# end: auto-generated types

	def autoname(self):
		abbreviation = frappe.db.get_value("Branch", self.branch, "abbreviation")
		if not abbreviation:
			frappe.throw("Setup Abbreviation in {}".format(frappe.get_desk_link("Branch", self.branch)))
		year_month = str(self.posting_date)[:7].replace('-', '')
		self.name = frappe.model.naming.make_autoname(f"{abbreviation}{year_month}.####")

	def validate(self):
		self.validate_abstract_bill_requires()
		self.set_activity_head()
		self.calculate_total_amount()
		self.set_approver()
		if not self.get("__islocal"):
			self.validate_fiscal_year()
			self.validate_file_index()
			self.validate_tax_exemption()

	def validate_fiscal_year(self):
		if not self.fiscal_year:
			frappe.throw("Please fiscal year")

	def before_submit(self):
		if not self.mode_of_payment:
			frappe.throw("Please set mode of payment before submit")
		self.validate_tax_exemption()
		self.generate_dispatch_number()

	def on_submit(self):
		self.post_journal_entry()
		self.update_reference_document()

	def on_cancel(self):
		self.update_reference_document(cancel=True)

	def validate_abstract_bill_requires(self):
		if not frappe.db.get_value("Company", self.company, "abstract_bill_required"):
			frappe.throw("Please check Abstract Bill Required for {} if requires Abstract Bill".format(frappe.get_desk_link("Company", self.company)))

	def update_reference_document(self, cancel=False):
		for item in self.items:
			# frappe.throw(str(item.reference_name))
			if item.reference_type == "Purchase Invoice" and item.reference_name:
				doc = frappe.get_doc("Purchase Invoice", item.reference_name)
				if cancel:
					doc.db_set("payment_status", "Unpaid")
				else:
					doc.db_set("payment_status", "Paid")

			# frappe.db.set_value('Purchase Invoice', item.reference_name, 'payment_status', status)


	def validate_tax_exemption(self):
		self.validate_file_index()
		for item in self.items:
			if not item.bill_date:
				frappe.throw("Please set Ref./Bill date in Row#{}.".format(frappe.bold(item.idx)))

			# Check whether supplier is in tax holiday or not
			if item.party_type == "Supplier":
				item.tax_exempted = self.check_tax_holiday(item.party_type, item.party, item.bill_date, item.idx)

	def generate_dispatch_number(self):
		current_count_series = frappe.db.get_value("Company", self.company, "count_series")
		new_count_series = int(current_count_series) + 1
		self.dispatch_number = f"{self.file_index}/{self.fiscal_year}/{new_count_series}"

		# Atomically update the count_series in the Company document
		frappe.db.set_value("Company", self.company, "count_series", new_count_series)

	def validate_file_index(self):
		if not self.file_index:
			frappe.throw("Please set <b>File Index</b> before submit")

	def check_tax_holiday(self, party_type, party, bill_date, idx):
		# Parameterized query to avoid SQL injection
		query = """
			SELECT 1 
			FROM `tabTax Holiday` th
			JOIN `tabSupplier` s ON s.tax_holiday = th.name
			WHERE s.name = %s
			AND %s BETWEEN th.from_date AND th.to_date
		"""
		
		# Execute the SQL query with parameters
		if frappe.db.sql(query, (party, bill_date), as_dict=True):
			return 1  # Set tax_exempted to 1 if a tax holiday exists
		else:
			return 0  # Set tax_exempted to 0 if no tax holiday exists

	def set_activity_head(self):
		for item in self.get("items"):
			# Get cost center code
			cc_code = frappe.db.get_value("Cost Center", item.cost_center, "cost_center_number")
			if not cc_code:
				frappe.throw("Please set cost center number for {}".format(
					frappe.get_desk_link("Cost Center", item.cost_center)
				))

			# Get sub-activity code
			sub_activity_result = frappe.db.sql("""
				SELECT code 
				FROM `tabSub Activity` 
				WHERE parent = %s AND business_activity = %s
			""", (item.cost_center, item.business_activity))
			if not sub_activity_result:
				frappe.throw("No sub activity in cost center {}".format(
					frappe.get_desk_link("Cost Center", item.cost_center)
				))
			sub_activity_code = sub_activity_result[0][0]
		
			if not sub_activity_result:
				frappe.throw("No sub-activity code found for the given cost center and business activity.")

			# Get budget type code
			budget_type_result = frappe.db.sql("""
				SELECT bt.budget_code 
				FROM `tabBudget Type` bt
				JOIN `tabAccount` a ON a.budget_type = bt.name 
				WHERE a.name = %s
			""", item.account)
			
			if not budget_type_result:
				frappe.throw("No budget type code found for account {}".format(
					frappe.get_desk_link("Account", item.account)
				))
			
			budget_type_code = budget_type_result[0][0]

			# Get account head code
			
			account_code = frappe.db.get_value("Account", item.account, "bank_account_no")
			
			if not account_code:
				frappe.throw("No account code found for account {}".format(item.account))

			# Construct object code
			object_code = f"{cc_code}.{sub_activity_code}/{budget_type_code}/{account_code}"
			
			item.activity_head = object_code

	def calculate_total_amount(self):
		total_amount = 0
		for a in self.get("items"):
			total_amount += flt(a.amount, 2)
		self.total_amount = total_amount

	def set_approver(self):
		self.approver = frappe.db.get_single_value("Accounts Settings", "abstract_bill_approver")
		self.approver_name = frappe.db.get_single_value("Accounts Settings", "ab_approver_name")

	def post_journal_entry(self):
		accounts = []

		# get credit account for Advance Recoup
		if self.reference_doctype == "Advance Recoup":
			advance_type = frappe.db.get_value("Advance Recoup", self.reference_name, "advance_type")
			account = frappe.db.get_value("Advance Type", advance_type, "account")
			if not account:
				frappe.throw("Please set account in {}".format(frappe.get_desk_link("Advance Type", self.reference_name)))
		else:
			if self.mode_of_payment == "Bank Entry":
				account = frappe.db.get_value("Company", self.company, "default_bank_account")
			elif self.mode_of_payment == "Cash Entry":
				account = frappe.db.get_value("Company", self.company, "default_cash_account")
			if not account:
				frappe.throw("Set Default {} Account in Company {}".format("Bank" if self.mode_of_payment=="Bank Entry" else "Cash", frappe.get_desk_link('company',self.company)))

		for item in self.items:
			accounts.append({
				"account": item.account,
				"debit_in_account_currency": flt(item.amount, 2) if self.currency == 'BTN' else flt(item.base_amount, 2),
				"cost_center": item.cost_center,
				"reference_type": self.doctype,
				"reference_name": self.name,
				"party_type": item.party_type,
				"party": item.party,
				"business_activity": item.business_activity,
			})

			accounts.append({
				"account": account,
				"credit_in_account_currency": flt(item.amount, 2) if self.currency == 'BTN' else flt(item.base_amount, 2),
				"cost_center": item.cost_center,
				"reference_type": self.doctype,
				"reference_name": self.name,
			})

		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permission = 1
		je.update({
			"doctype": "Journal Entry",
			"posting_date": self.posting_date,
			"branch": self.branch,
			"voucher_type": self.mode_of_payment,
			"naming_series": "Bank Payment Voucher" if self.mode_of_payment == "Bank Entry" else "Cash Payment Voucher",
			"company": self.company,
			"reference_doctype": self.doctype,
			"reference_name": self.name,
			"accounts": accounts
		})
		je.insert()
		je.submit()
		self.db_set('journal_entry', je.name)
		self.db_set("journal_entry_status", "Forwarded to accounts for processing payment on {0}".format(now_datetime().strftime('%Y-%m-%d %H:%M:%S')))
		frappe.msgprint(_('Journal Entry {0} posted to accounts').format(frappe.get_desk_link("Journal Entry", je.name)))
  
	@frappe.whitelist()
	def get_transactions_detail(self):
		if self.transaction_type == "Purchase Invoice":
			data = frappe.db.sql('''
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
							`tabAbstract Bill Item` abi 
							ON pi.name = abi.reference_name
						WHERE 
							pi.docstatus = 1 and pi.payment_status="Unpaid"
							and settle_from_advance = 0
							AND (abi.reference_name IS NULL or abi.docstatus = 2);
       
						''',as_dict=True)
			self.set('items',[])
			
			if not data:
				frappe.throw(_("No Transactions Found"))

			for d in data:
				d['party_type'] = 'Supplier'
				d['reference_type'] = 'Purchase Invoice'
				self.append('items', d)

			return True

@frappe.whitelist()
def get_fiscal_year(doctype, txt, searchfield, start, page_len, filters):
    cond = ""
    if filters and filters.get("company"):
        cond = "and t2.company = %(company)s"

    return frappe.db.sql(
        f"""
        select t1.name 
        from `tabFiscal Year` t1, `tabFiscal Year Company` t2
        where t1.name = t2.parent and t1.`{searchfield}` LIKE %(txt)s {cond}
        order by t1.name 
        limit %(page_len)s offset %(start)s
        """,
        {
            "txt": "%" + txt + "%",
            "company": filters.get("company"),
            "start": start,
            "page_len": page_len
        }
    )