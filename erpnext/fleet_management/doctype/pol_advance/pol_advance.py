# # Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt

# import frappe
# from frappe import _
# from frappe.model.document import Document
# from erpnext.accounts.doctype.business_activity.business_activity import get_default_ba
# from frappe.utils import money_in_words, cstr, flt, fmt_money, formatdate, getdate, nowdate, cint, get_link_to_form, now_datetime, get_datetime
# from frappe.model.mapper import get_mapped_doc
# from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states
# from frappe import _, qb, throw, bold
# from erpnext.accounts.party import get_party_account
# from erpnext.controllers.accounts_controller import AccountsController
# from erpnext.accounts.general_ledger import (
# 	get_round_off_account_and_cost_center,
# 	make_gl_entries,
# 	make_reverse_gl_entries,
# 	merge_similar_entries,
# )

# class POLAdvance(AccountsController):
# 	# begin: auto-generated types
# 	# This code is auto-generated. Do not modify anything in this block.

# 	from typing import TYPE_CHECKING

# 	if TYPE_CHECKING:
# 		from frappe.types import DF

# 		adjusted_amount: DF.Currency
# 		advance_limit: DF.Currency
# 		amended_from: DF.Link | None
# 		amount: DF.Currency
# 		approver: DF.Link | None
# 		approver_designation: DF.Link | None
# 		approver_name: DF.Data | None
# 		balance_amount: DF.Currency
# 		book_type: DF.Literal["", "Own", "Common"]
# 		branch: DF.Link | None
# 		cheque_date: DF.Date | None
# 		cheque_no: DF.Data | None
# 		company: DF.Link
# 		cost_center: DF.Link | None
# 		credit_account: DF.Link | None
# 		currency: DF.Link
# 		entry_date: DF.Date
# 		equipment: DF.Link | None
# 		equipment_category: DF.Link | None
# 		equipment_type: DF.Link | None
# 		fuel_book: DF.Link
# 		fuelbook_branch: DF.Link | None
# 		is_opening: DF.Check
# 		journal_entry: DF.Data | None
# 		party: DF.Data
# 		party_type: DF.Link
# 		pay_to_recd_from: DF.Data | None
# 		payment_status: DF.Literal["", "Paid", "Unpaid", "Submitted", "Partly Paid", "Draft", "Cancelled"]
# 		select_cheque_lot: DF.Link | None
# 		use_cheque_lot: DF.Check
# 		use_common_fuelbook: DF.Check
# 		user_remark: DF.SmallText | None
# 		workflow_state: DF.Data | None
# 	# end: auto-generated types
# 	def validate(self):
# 		# if flt(self.is_opening) == 0:
# 		# 	validate_workflow_states(self)
# 		self.set_advance_limit()
# 		self.posting_date = self.entry_date
# 		self.validate_amount()

# 		self.credit_account = frappe.db.get_value("Branch", self.fuelbook_branch, "expense_bank_account")

# 		# if flt(self.is_opening) == 0 and self.workflow_state != "Approved" :
# 		# 	notify_workflow_states(self)
	
# 	def on_submit(self): 
# 		if not self.is_opening:
# 			self.post_journal_entry()

# 	def before_cancel(self):
# 		if self.is_opening:
# 			return
# 		if frappe.db.exists("Journal Entry",self.journal_entry):
# 			doc = frappe.get_doc("Journal Entry", self.journal_entry)
# 			if doc.docstatus != 2:
# 				frappe.throw("Journal Entry exists for this transaction {}".format(frappe.get_desk_link("Journal Entry",self.journal_entry)))
				
# 	def on_cancel(self):
# 		self.ignore_linked_doctypes = ("GL Entry", "Stock Ledger Entry", "Payment Ledger Entry")

# 	@frappe.whitelist()
# 	def get_fuelbook(self):
# 		if not self.equipment:
# 			frappe.throw("Equipment or Fuel book is missing")
# 		return frappe.db.get_value("Equipment", self.equipment, "fuelbook")

# 	@frappe.whitelist()
# 	def set_advance_limit(self):
# 		if cint(self.use_common_fuelbook) == 1:
# 			if not self.fuel_book:
# 				frappe.throw("Fuel book is missing")
# 			if flt(self.advance_limit) <= 0 :
# 				self.advance_limit = frappe.db.get_value("Fuelbook", self.fuel_book, "expense_limit")
# 		else:
# 			if not self.equipment:
# 				frappe.throw("Equipment or Fuel book is missing")

# 			if flt(self.advance_limit) <= 0 and self.equipment_type:
# 				self.advance_limit = frappe.db.get_value("Fuelbook", self.fuel_book, "expense_limit")
	
# 	@frappe.whitelist()
# 	def set_auto_advance_amount(self):
# 		if not self.fuel_book:
# 			frappe.throw("Fuel book is missing")
		
# 		if not self.equipment:
# 			frappe.throw("Equipment or Fuel book is missing")
		
# 		advance_amount = frappe.db.sql("""
# 							SELECT SUM(amount) - sum(adjusted_amount) as bal
# 							FROM `tabPOL Advance`
# 							WHERE docstatus = 1 AND equipment = '{0}' 
# 							AND fuel_book = '{1}' AND entry_date < '{2}'
# 						""".format(self.equipment, self.fuel_book, self.entry_date), as_list=True)

# 		if advance_amount and advance_amount[0][0]:
# 			new_amount = self.advance_limit - flt(advance_amount[0][0])
# 			if new_amount > 0:
# 				return self.advance_limit - flt(advance_amount[0][0])
# 			else:
# 				return 0
# 	# @frappe.whitelist()
# 	# def make_pol_receive_from_advance(pol_advance):
# 	# 	source = frappe.get_doc("POL Advance", pol_advance)
# 	# 	new_doc = frappe.new_doc("POL Receive")
# 	# 	new_doc.set_missing_values(source)
# 	# 	new_doc.equipment = source.equipment
# 	# 	new_doc.branch = source.fuelbook_branch or source.branch
# 	# 	new_doc.fuelbook = source.fuel_book
# 	# 	new_doc.book_type = source.book_type
# 	# 	new_doc.cost_center = source.cost_center
# 	# 	new_doc.supplier = source.party
# 	# 	new_doc.direct_consumption = 1 if source.book_type == "Own" else 0
# 	# 	return new_doc.as_dict()		
	
# 	def post_journal_entry(self):
# 		if self.is_opening:
# 			return
# 		if not self.amount:
# 			frappe.throw(_("Amount should be greater than zero"))
			
# 		default_ba = get_default_ba()
		
# 		credit_account = frappe.db.get_value("Branch",self.fuelbook_branch,"expense_bank_account")
# 		advance_account = frappe.db.get_value("Company", self.company, "pol_advance_account")
# 		if not advance_account:
# 			frappe.throw("Please Set Account for POL Advance Account in Company")
# 		if not credit_account:
# 			frappe.throw("Credit Account is mandatory")
		
# 		r = []
# 		if self.cheque_no:
# 			if self.cheque_date:
# 				r.append(_('Reference #{0} dated {1}').format(self.cheque_no, formatdate(self.cheque_date)))
# 			else:
# 				msgprint(_("Please enter Cheque Date date"), raise_exception=frappe.MandatoryError)
		
# 		if self.user_remark:
# 			r.append(_("Note: {0}").format(self.user_remark))

# 		remarks = ("").join(r) #User Remarks is not mandatory
		
# 		# Posting Journal Entry
# 		je = frappe.new_doc("Journal Entry")
# 		je.flags.ignore_permissions=1
# 		je.update({
# 			"doctype": "Journal Entry",
# 			"voucher_type": "Bank Entry",
# 			"naming_series": "Bank Payment Voucher",
# 			"title": "POL Advance - " + self.equipment if cint(self.use_common_fuelbook) == 0 else self.fuel_book,
# 			"user_remark": "Note: " + "POL Advance - " + self.equipment if cint(self.use_common_fuelbook) == 0 else self.fuel_book,
# 			"posting_date": self.posting_date,
# 			"company": self.company,
# 			"total_amount_in_words": money_in_words(self.amount),
# 			"branch": self.fuelbook_branch,
# 		})

# 		je.append("accounts",{
# 			"account": credit_account,
# 			"credit_in_account_currency": self.amount,
# 			"cost_center": self.cost_center,
# 			"reference_type": "POL Advance",
# 			"reference_name": self.name,
# 			"business_activity": default_ba
# 		})

# 		je.append("accounts",{
# 			"account": advance_account,
# 			"debit_in_account_currency": self.amount,
# 			"cost_center": self.cost_center,
# 			"party_check": 0,
# 			"party_type": "Supplier",
# 			"party": self.party,
# 			"business_activity": default_ba
# 		})

# 		je.insert()
# 		#Set a reference to the claim journal entry
# 		self.db_set("journal_entry",je.name)
# 		frappe.msgprint(_('Journal Entry {0} posted to accounts').format(frappe.get_desk_link("Journal Entry",je.name)))
	
# 	def validate_amount(self):
# 		if flt(self.amount) <= 0:
# 			frappe.throw("Amount cannot be less than or equal to Zero")
# 		if cint(self.use_common_fuelbook) == 0 and flt(self.amount) > flt(self.advance_limit):
# 			frappe.throw("Amount cannot be greater than advance limit "+str(self.advance_limit))
# 		if cint(self.is_opening) == 0 :
# 			self.outstanding_amount = self.amount
# # @frappe.whitelist()
# # def make_pol_receive_from_advance(source_name, target_doc=None):
# # 	def update_item(source_item, target_item, source_parent):
# # 		"""
# # 		Map child table items if needed.
# # 		Copy amount and link to advance item
# # 		"""
# # 		# target_item.qty = flt(source_item.amount) 
# # 		# target_item.amount = flt(source_item.amount)
# # 		# target_item.pol_advance_item = source_item.name

# # 	def set_missing_values(source_doc, target_doc):
# # 		target_doc.branch = source_doc.fuelbook_branch
# # 		if source_doc.equipment:
# # 			pol_type = frappe.db.get_value("Equipment", source_doc.equipment, "hsd_type")
# # 			if pol_type:
# # 				target_doc.pol_type = pol_type


# # 	# Map POL Advance -> POL Receive
# # 	doc = get_mapped_doc(
# # 		"POL Advance",
# # 		source_name,
# # 		{
# # 			"POL Advance": {
# # 				"doctype": "POL Receive",
# # 				"field_map": {
# # 					"equipment": "equipment",
# # 					"fuel_book": "fuelbook",
# # 					"cost_center": "cost_center",
# # 					"party": "supplier",
# # 				},
# # 				"validation": {"docstatus": ["=", 1]},
# # 			},
# # 			"POL Advance Item": {
# # 				"doctype": "POL Receive Item",
# # 				"field_map": {
# # 					"item_name": "pol_type",
# # 					"amount": "amount",
# # 				},
# # 				"postprocess": update_item,
# # 			},
# # 		},
# # 		target_doc,
# # 		set_missing_values,
# # 	)

# # 	return doc.as_dict()

# def get_permission_query_conditions(user):
# 	if not user: user = frappe.session.user
# 	user_roles = frappe.get_roles(user)

# 	if user == "Administrator" or "System Manager" in user_roles: 
# 		return

# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from erpnext.accounts.doctype.business_activity.business_activity import get_default_ba
from frappe.utils import money_in_words, cstr, flt, fmt_money, formatdate, getdate, nowdate, cint, get_link_to_form, now_datetime, get_datetime
from frappe.model.mapper import get_mapped_doc
from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states
from frappe import _, qb, throw, bold
from erpnext.accounts.party import get_party_account
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.accounts.general_ledger import (
	get_round_off_account_and_cost_center,
	make_gl_entries,
	make_reverse_gl_entries,
	merge_similar_entries,
)

class POLAdvance(AccountsController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		adjusted_amount: DF.Currency
		advance_limit: DF.Currency
		amended_from: DF.Link | None
		amount: DF.Currency
		approver: DF.Link | None
		approver_designation: DF.Link | None
		approver_name: DF.Data | None
		balance_amount: DF.Currency
		book_type: DF.Literal["", "Own", "Common", "General Pol"]
		branch: DF.Link | None
		cheque_date: DF.Date | None
		cheque_no: DF.Data | None
		company: DF.Link
		cost_center: DF.Link | None
		credit_account: DF.Link | None
		currency: DF.Link
		entry_date: DF.Date
		equipment: DF.Link | None
		equipment_category: DF.Link | None
		equipment_type: DF.Link | None
		fuel_book: DF.Link
		fuelbook_branch: DF.Link | None
		is_opening: DF.Check
		journal_entry: DF.Data | None
		party: DF.Link
		party_type: DF.Link
		pay_to_recd_from: DF.Data | None
		payment_status: DF.Literal["", "Paid", "Unpaid", "Submitted", "Partly Paid", "Draft", "Cancelled"]
		select_cheque_lot: DF.Link | None
		use_cheque_lot: DF.Check
		use_common_fuelbook: DF.Check
		user_remark: DF.SmallText | None
		workflow_state: DF.Data | None
	# end: auto-generated types
	def validate(self):
		# if flt(self.is_opening) == 0:
		# 	validate_workflow_states(self)
		self.set_advance_limit()
		self.posting_date = self.entry_date
		self.validate_amount()

		self.credit_account = frappe.db.get_value("Branch", self.fuelbook_branch, "expense_bank_account")

		# if flt(self.is_opening) == 0 and self.workflow_state != "Approved" :
		# 	notify_workflow_states(self)
	
	def on_submit(self): 
		if not self.is_opening:
			self.post_journal_entry()

	def before_cancel(self):
		if self.is_opening:
			return
		if frappe.db.exists("Journal Entry",self.journal_entry):
			doc = frappe.get_doc("Journal Entry", self.journal_entry)
			if doc.docstatus != 2:
				frappe.throw("Journal Entry exists for this transaction {}".format(frappe.get_desk_link("Journal Entry",self.journal_entry)))
				
	def on_cancel(self):
		self.ignore_linked_doctypes = ("GL Entry", "Stock Ledger Entry", "Payment Ledger Entry")

	@frappe.whitelist()
	def get_fuelbook(self):
		if not self.equipment:
			frappe.throw("Equipment or Fuel book is missing")
		return frappe.db.get_value("Equipment", self.equipment, "fuelbook")

	@frappe.whitelist()
	def set_advance_limit(self):
		if cint(self.use_common_fuelbook) == 1:
			if not self.fuel_book:
				frappe.throw("Fuel book is missing")
			if flt(self.advance_limit) <= 0 :
				self.advance_limit = frappe.db.get_value("Fuelbook", self.fuel_book, "expense_limit")
		else:
			if self.book_type == "General Pol":
				general_book = frappe.db.get_value("Fuelbook", {"type": "General Pol"}, "name")
				if not general_book:
					frappe.throw("No General Fuel book found")
				if flt(self.advance_limit) <= 0:
					self.advance_limit = frappe.db.get_value("Fuelbook", general_book, "expense_limit")
			
        # For other equipment types, equipment must exist
			else:
				if not self.equipment:
					frappe.throw("Equipment or Fuel book is missing")
				# Get fuel book linked to equipment
				fuelbook = frappe.db.get_value("Equipment", self.equipment, "fuelbook")
				if not fuelbook:
					frappe.throw("No Fuel book linked to this equipment")
				if flt(self.advance_limit) <= 0:
					self.advance_limit = frappe.db.get_value("Fuelbook", fuelbook, "expense_limit")
			# if not self.equipment:
			# 	frappe.throw("Equipment or Fuel book is missing")

			# if flt(self.advance_limit) <= 0 and self.equipment_type:
			# 	self.advance_limit = frappe.db.get_value("Fuelbook", self.fuel_book, "expense_limit")
	
	@frappe.whitelist()
	def set_auto_advance_amount(self):
		if not self.fuel_book:
			frappe.throw("Fuel book is missing")
		
		if not (self.equipment or  self.fuel_book):
			frappe.throw("Equipment or Fuel book is missing")
		
		advance_amount = frappe.db.sql("""
							SELECT SUM(amount) - sum(adjusted_amount) as bal
							FROM `tabPOL Advance`
							WHERE docstatus = 1 AND equipment = '{0}' 
							AND fuel_book = '{1}' AND entry_date < '{2}'
						""".format(self.equipment, self.fuel_book, self.entry_date), as_list=True)

		if advance_amount and advance_amount[0][0]:
			new_amount = self.advance_limit - flt(advance_amount[0][0])
			if new_amount > 0:
				return self.advance_limit - flt(advance_amount[0][0])
			else:
				return 0
	# @frappe.whitelist()
	# def make_pol_receive_from_advance(pol_advance):
	# 	source = frappe.get_doc("POL Advance", pol_advance)
	# 	new_doc = frappe.new_doc("POL Receive")
	# 	new_doc.set_missing_values(source)
	# 	new_doc.equipment = source.equipment
	# 	new_doc.branch = source.fuelbook_branch or source.branch
	# 	new_doc.fuelbook = source.fuel_book
	# 	new_doc.book_type = source.book_type
	# 	new_doc.cost_center = source.cost_center
	# 	new_doc.supplier = source.party
	# 	new_doc.direct_consumption = 1 if source.book_type == "Own" else 0
	# 	return new_doc.as_dict()		
	
	def post_journal_entry(self):
		if self.is_opening:
			return
		if not self.amount:
			frappe.throw(_("Amount should be greater than zero"))
			
		default_ba = get_default_ba()
		
		credit_account = frappe.db.get_value("Branch",self.fuelbook_branch,"expense_bank_account")
		advance_account = frappe.db.get_value("Company", self.company, "pol_advance_account")
		if not advance_account:
			frappe.throw("Please Set Account for POL Advance Account in Company")
		if not credit_account:
			frappe.throw("Credit Account is mandatory")
		
		r = []
		if self.cheque_no:
			if self.cheque_date:
				r.append(_('Reference #{0} dated {1}').format(self.cheque_no, formatdate(self.cheque_date)))
			else:
				msgprint(_("Please enter Cheque Date date"), raise_exception=frappe.MandatoryError)
		
		if self.user_remark:
			r.append(_("Note: {0}").format(self.user_remark))

		remarks = ("").join(r) #User Remarks is not mandatory
		
		# Posting Journal Entry
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions=1
		ref_name = self.equipment if self.equipment else self.fuel_book or "General Pol"
		je.update({
			"doctype": "Journal Entry",
			"voucher_type": "Bank Entry",
			"naming_series": "Bank Payment Voucher",
			"title": f"POL Advance - {ref_name}",
    		"user_remark": f"Note: POL Advance - {ref_name}",
			"posting_date": self.posting_date,
			"company": self.company,
			"total_amount_in_words": money_in_words(self.amount),
			"branch": self.fuelbook_branch,
		})

		je.append("accounts",{
			"account": credit_account,
			"credit_in_account_currency": self.amount,
			"cost_center": self.cost_center,
			"reference_type": "POL Advance",
			"reference_name": self.name,
			"business_activity": default_ba
		})

		je.append("accounts",{
			"account": advance_account,
			"debit_in_account_currency": self.amount,
			"cost_center": self.cost_center,
			"party_check": 0,
			"party_type": "Supplier",
			"party": self.party,
			"business_activity": default_ba
		})

		je.insert()
		#Set a reference to the claim journal entry
		self.db_set("journal_entry",je.name)
		frappe.msgprint(_('Journal Entry {0} posted to accounts').format(frappe.get_desk_link("Journal Entry",je.name)))
	
	def validate_amount(self):
		if flt(self.amount) <= 0:
			frappe.throw("Amount cannot be less than or equal to Zero")
		if cint(self.use_common_fuelbook) == 0 and flt(self.amount) > flt(self.advance_limit):
			frappe.throw("Amount cannot be greater than advance limit "+str(self.advance_limit))
		if cint(self.is_opening) == 0 :
			self.outstanding_amount = self.amount
# @frappe.whitelist()
# def make_pol_receive_from_advance(source_name, target_doc=None):
# 	def update_item(source_item, target_item, source_parent):
# 		"""
# 		Map child table items if needed.
# 		Copy amount and link to advance item
# 		"""
# 		# target_item.qty = flt(source_item.amount) 
# 		# target_item.amount = flt(source_item.amount)
# 		# target_item.pol_advance_item = source_item.name

# 	def set_missing_values(source_doc, target_doc):
# 		target_doc.branch = source_doc.fuelbook_branch
# 		if source_doc.equipment:
# 			pol_type = frappe.db.get_value("Equipment", source_doc.equipment, "hsd_type")
# 			if pol_type:
# 				target_doc.pol_type = pol_type


# 	# Map POL Advance -> POL Receive
# 	doc = get_mapped_doc(
# 		"POL Advance",
# 		source_name,
# 		{
# 			"POL Advance": {
# 				"doctype": "POL Receive",
# 				"field_map": {
# 					"equipment": "equipment",
# 					"fuel_book": "fuelbook",
# 					"cost_center": "cost_center",
# 					"party": "supplier",
# 				},
# 				"validation": {"docstatus": ["=", 1]},
# 			},
# 			"POL Advance Item": {
# 				"doctype": "POL Receive Item",
# 				"field_map": {
# 					"item_name": "pol_type",
# 					"amount": "amount",
# 				},
# 				"postprocess": update_item,
# 			},
# 		},
# 		target_doc,
# 		set_missing_values,
# 	)

# 	return doc.as_dict()
@frappe.whitelist()
def get_supplier_from_fuelbook(fuel_book):
    """Return a list of suppliers linked to a fuel_book"""
    fb = frappe.get_doc("Fuelbook", fuel_book)
    if getattr(fb, "supplier", None):
        return [fb.supplier]
    if getattr(fb, "suppliers", None):
        return [d.supplier for d in fb.suppliers]
    return []

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles: 
		return