# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, money_in_words
from erpnext.accounts.doctype.business_activity.business_activity import get_default_ba
from erpnext.accounts.party import get_party_account

class InsuranceandRegistration(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.bluebook_and_emission.bluebook_and_emission import BluebookandEmission
		from erpnext.fleet_management.doctype.claim_details.claim_details import ClaimDetails
		from erpnext.fleet_management.doctype.insurance_details.insurance_details import InsuranceDetails
		from erpnext.fleet_management.doctype.registration_details.registration_details import RegistrationDetails
		from frappe.types import DF

		amended_from: DF.Link | None
		asset: DF.Link | None
		asset_category: DF.Data | None
		asset_name: DF.Data | None
		asset_sub_category: DF.Data | None
		branch: DF.Link | None
		claim_item: DF.Table[ClaimDetails]
		company: DF.Link | None
		cost_center: DF.Link | None
		equipment: DF.Link | None
		imprest_party: DF.DynamicLink | None
		insurance_for: DF.Literal["", "Vehicle", "Asset"]
		insurance_item: DF.Table[InsuranceDetails]
		items: DF.Table[BluebookandEmission]
		party_type: DF.Literal["", "Employee", "Agency"]
		posting_date: DF.Date | None
		registration_item: DF.Table[RegistrationDetails]
		settle_from_advance: DF.Check
		total_amount: DF.Data | None
		vehicle_model: DF.Data | None
		vehicle_type: DF.Link | None
	# end: auto-generated types
	def validate(self):
		self.prevent_row_remove()
		self.calculate_total_amount()
  
	def calculate_total_amount(self):
		total = 0;
		for i in self.insurance_item:
			total += int(i.total_amount)
		for i in self.registration_item:
			total += int(i.registration_amount)
		for i in self.items:
			total += int(i.total_amount)
		self.set('total_amount',total)
		# frappe.throw(str(total))
			

	def prevent_row_remove(self):
		unsafed_record = [d.name for d in self.insurance_item]
		if flt(len(unsafed_record)) <= 0:
			unsafed_record = ["Dummy"]
		for d in frappe.db.sql("select name, journal_entry, idx from `tabInsurance Details` where parent = '{}'".format(self.name),as_dict=True):
			if d.name not in unsafed_record and d.journal_entry:
				je = frappe.get_doc("Journal Entry",d.journal_entry)
				if je.docstatus != 2:
					frappe.throw("You cannot delete row {} from Insurance Detail as \
						accounting entry is booked".format(frappe.bold(d.idx)))

		unsafed_record = [d.name for d in self.items]
		if flt(len(unsafed_record)) <= 0:
			unsafed_record = ["Dummy"]
		for d in frappe.db.sql("select name, journal_entry, idx from `tabBluebook and Emission` where parent = '{}'".format(self.name),as_dict=True):
			if d.name not in unsafed_record and d.journal_entry:
				je = frappe.get_doc("Journal Entry",d.journal_entry)
				if je.docstatus != 2:
					frappe.throw("You cannot delete row {} from Bluebook Fitness \
							and Emission Details as accounting entry is booked".format(frappe.bold(d.idx)))
		
	@frappe.whitelist()
	def create_je(self, args):
		if args.journal_entry and frappe.db.exists("Journal Entry",args.journal_entry):
			doc = frappe.get_doc("Journal Entry", args.journal_entry)
			if doc.docstatus != 2:
				frappe.throw("Journal Entry exists for this transaction {}".format(frappe.get_desk_link("Journal Entry",args.journal_entry)))
			
		if flt(args.total_amount) <= 0:
			frappe.throw(_("Amount should be greater than zero"))
			
		default_bank_account = frappe.db.get_value("Branch", self.branch,'expense_bank_account')

		# Posting Journal Entry
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions=1
		if args.get("type") == "Insurance":
			debit_account 	= get_party_account("Supplier",args.get("party"),self.company, is_advance = True)
			posting_date = args.get("insured_date")
		else:
			posting_date = args.get("receipt_date")
			debit_account 	= frappe.db.get_value("Company", self.company,'repair_and_service_expense_account')
			if not debit_account:
				frappe.throw("Setup Fleet Expense Account in Company".format())
		if not default_bank_account:
			frappe.throw("Setup Default Bank Account in Branch {}".format(self.branch))
		posting_date
		je.update({
			"doctype": "Journal Entry",
			"voucher_type": "Bank Entry",
			"naming_series": "Bank Payment Voucher",
			"title": args.type + " Charge - " + self.equipment,
			"user_remark": "Note: " + args.type + " Charge paid against Vehicle " + self.equipment,
			"posting_date": posting_date,
			"company": self.company,
			"total_amount_in_words": money_in_words(args.total_amount),
			"branch": self.branch,
		})
		je.append("accounts",{
			"account": debit_account,
			"debit_in_account_currency": args.total_amount,
			"cost_center": frappe.db.get_value('Branch',self.branch,'cost_center'),
			"party_check": 0,
			"party_type": "Supplier",
			"party": args.party,
			"reference_type": self.doctype,
			"reference_name": self.name
			})
		je.append("accounts",{
			"account": default_bank_account,
			"credit_in_account_currency": args.total_amount,
			"cost_center": frappe.db.get_value('Branch',self.branch,'cost_center')
		})
		je.insert()
		frappe.msgprint(_('Journal Entry {0} posted to accounts').format(frappe.get_desk_link("Journal Entry",je.name)))
		return je.name
		#Set a reference to the claim journal entry
