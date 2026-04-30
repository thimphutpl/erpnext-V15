# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr, flt, fmt_money, formatdate, getdate, get_datetime, nowdate
from frappe.desk.reportview import get_match_cond
from erpnext.custom_utils import check_uncancelled_linked_doc, check_future_date
from frappe.model.mapper import get_mapped_doc
from erpnext.controllers.accounts_controller import AccountsController


class EquipmentHiringForm(AccountsController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.hiring_approval_details.hiring_approval_details import HiringApprovalDetails
		from erpnext.fleet_management.doctype.hiring_request_details.hiring_request_details import HiringRequestDetails
		from frappe.types import DF

		address: DF.Data | None
		advance_amount: DF.Currency
		advance_journal: DF.Link | None
		amended_from: DF.Link | None
		apply_gst: DF.Check
		approved_items: DF.Table[HiringApprovalDetails]
		branch: DF.Link
		charges_type: DF.Literal["", "Hire Charge Receivable", "Hire Charge Payable"]
		contact_number: DF.Data | None
		cost_center: DF.Link
		customer: DF.Link | None
		customer_branch: DF.ReadOnly | None
		customer_cost_center: DF.ReadOnly | None
		end_date: DF.Date | None
		er_reference: DF.Link | None
		gst_account: DF.Link | None
		gst_amount: DF.Currency
		hiring_status: DF.Check
		location: DF.Link | None
		payment_completed: DF.Check
		private: DF.Literal["Own", "Private"]
		private_customer_address: DF.SmallText | None
		private_customer_name: DF.Data | None
		project: DF.Link | None
		rate: DF.Currency
		rate_based_on: DF.Literal["", "Daily", "Kilometer", "Lumpsum", "Per Hour", "Per Pack"]
		reading_based_on: DF.Data | None
		request_date: DF.Date
		request_items: DF.Table[HiringRequestDetails]
		start_date: DF.Date | None
		supplier: DF.Link | None
		tc_name: DF.Link | None
		terms: DF.TextEditor | None
		total_hiring_amount: DF.Currency
		workflow_state: DF.Link | None
	# end: auto-generated types
	def validate(self):
		check_future_date(self.request_date)
		self.check_date_approval()
		self.check_duplicate()
		self.calculate_totals()

	def validate_date(self, a):
		from_date = get_datetime(str(a.from_date) + ' ' + str(a.from_time))
		to_date = get_datetime(str(a.to_date) + ' ' + str(a.to_time))
		if to_date < from_date:
			frappe.throw("From Date/Time cannot be greater than To Date/Time")

	def before_submit(self):
		self.check_equipment_free()
		if self.private == "Private" and self.advance_amount <= 0:
			frappe.throw("For Private Customers, Advance Amount is Required!")

		if not self.approved_items:
			frappe.throw("Cannot submit hiring form without Approved Items")

	# def before_submit(self):
	# 	self.check_equipment_free()		
	def on_cancel(self):
		self.ignore_linked_doctypes = ("Journal Entry","GL Entry", "Stock Ledger Entry","Payment Ledger Entry", "Hire Charge Invoice", "Vehicle Logbook")
		super().on_cancel()
		self.update_equipment_request(0)

	def on_submit(self):
		self.assign_hire_form_to_equipment()
		if self.advance_amount > 0:
			self.post_journal_entry()
		self.update_equipment_request(1)
		#self.update_journal()

	def before_cancel(self):		
		# check_uncancelled_linked_doc(self.doctype, self.name)
		cl_status = frappe.db.get_value("Journal Entry", self.advance_journal, "docstatus")
		if cl_status and cl_status != 2:
			frappe.throw("You need to cancel the journal entry related to this job card first!")
	
		frappe.db.sql("delete from `tabEquipment Reservation Entry` where ehf_name = \'"+ str(self.name) +"\'")	
		self.db_set("advance_journal", '')


	
	def update_journal(self):
		for a in self.balance_advance_details:
			frappe.db.sql("UPDATE `tabJournal Entry Account` SET `reference_name` = \'" + str(self.name) + "\' WHERE name = \'" + str(a.reference_row) + "\'")

	def update_equipment_request(self, action):
		if action == 'Cancel':
			ehf = ''
		else:
			ehf = self.name
		if self.er_reference:
			er = frappe.get_doc("Equipment Request", self.er_reference)
			er.db_set("ehf",ehf)

	def check_date_approval(self):
		for a in self.approved_items:
			self.validate_date(a)

	def check_duplicate(self):
		for a in self.approved_items:
			for b in self.approved_items:
				if a.equipment == b.equipment and a.idx != b.idx:
					frappe.throw("Duplicate entries for equipments in row " + str(a.idx) + " and " + str(b.idx))

	# def calculate_totals(self):
	# 	if self.approved_items:
	# 		total = 0
	# 		for a in self.approved_items:
	# 			total += flt(a.grand_total)
	# 		self.total_hiring_amount = total
	# 		if self.private == "Private" and not self.advance_amount:
	# 			self.advance_amount = total	

	def calculate_totals(self):
		if self.approved_items:
			total = 0
			for item in self.approved_items:
				# Check if lumpsum_rate exists for the item in the child table
				if flt(item.lumpsum_rate):
					item.grand_total = flt(item.lumpsum_rate)
				else:
					# Keep grand_total as it is if no lumpsum_rate is provided
					item.grand_total = item.grand_total or 0
				
				# Add the grand_total of the item to the total
				total += flt(item.grand_total)

			# Update the total_hiring_amount
			self.total_hiring_amount = total

			# If the form is private and advance_amount is not set, set it to total_hiring_amount
			if self.private == "Private" and not self.advance_amount:
				self.advance_amount = self.total_hiring_amount



	def assign_hire_form_to_equipment(self):
		for a in self.approved_items:
			doc = frappe.new_doc("Equipment Reservation Entry")
			doc.flags.ignore_permissions = 1 
			doc.equipment = a.equipment
			doc.reason = "Hire"
			doc.ehf_name = self.name
			doc.place = a.place
			doc.from_date = a.from_date
			doc.to_date = a.to_date
			doc.hours = a.total_hours
			doc.to_time = a.to_time
			doc.from_time = a.from_time
			doc.submit()	

	def check_equipment_free(self):
		for a in self.approved_items:
			ec = frappe.db.get_value("Equipment Category", frappe.db.get_value("Equipment", a.equipment, "equipment_category"), "allow_hire")
			if ec:
				pass
			else:
				from_datetime = str(get_datetime(str(a.from_date) + ' ' + str(a.from_time))) 
				to_datetime = str(get_datetime(str(a.to_date) + ' ' + str(a.to_time)))
				result = frappe.db.sql("""
										select ehf_name
										from `tabEquipment Reservation Entry`
										where equipment = '{0}'
										and docstatus = 1
										and ('{1}' between concat(from_date,' ',from_time) and concat(to_date,' ',to_time)
												or
												'{2}' between concat(from_date,' ',from_time) and concat(to_date,' ',to_time)
												or
												('{3}' <= concat(from_date,' ',from_time) and '{4}' >= concat(to_date,' ',to_time))
										)
								""".format(a.equipment, from_datetime, to_datetime, from_datetime, to_datetime), as_dict=True)
				for r in result:
					frappe.throw(_("The equipment {0} is already in use from by {1}").format(a.equipment, r.ehf_name))	

# make necessary journal entry
	##
	def post_journal_entry(self):
		advance_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_advance_account")
		revenue_bank = frappe.db.get_value("Branch", self.branch, "revenue_bank_account")
		
		if revenue_bank and advance_account:
			# frappe.throw("hhhhhhhhh")
			je = frappe.new_doc("Journal Entry")
			je.flags.ignore_permissions = 1 
			je.title = "Advance for Equipment Hire (" + self.name + ")"
			je.voucher_type = 'Bank Entry'
			je.naming_series = 'Bank Receipt Voucher'
			je.remark = 'Advance payment against : ' + self.name
			je.posting_date = frappe.utils.nowdate()
			je.branch = self.branch

			je.append("accounts", {
				"account": advance_account,
				"party_type": "Customer",
				"party": self.customer,
				"reference_type": "Equipment Hiring Form",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.advance_amount) if self.apply_gst == 1 and self.charges_type == "Hire Charge Payable" else flt(self.total_hiring_amount),
				"credit": flt(self.advance_amount) if self.apply_gst == 1 and self.charges_type == "Hire Charge Payable" else flt(self.total_hiring_amount),
				"is_advance": 'Yes'
			})

			je.append("accounts", {
				"account": revenue_bank,
				"cost_center": self.cost_center,
				"debit_in_account_currency": flt(self.advance_amount) if self.apply_gst == 1 and self.charges_type == "Hire Charge Receivable" else flt(self.total_hiring_amount),
				"debit": flt(self.advance_amount) if self.apply_gst == 1  and self.charges_type == "Hire Charge Receivable" else flt(self.total_hiring_amount),
			})
			if self.apply_gst == 1:
				dr_or_cr = "debit" if self.charges_type == "Hire Charge Payable" else "credit"
				je.append("accounts", {
					"account": self.gst_account,
					"cost_center": self.cost_center,
					dr_or_cr + "_in_account_currency": flt(self.gst_amount),
					dr_or_cr: flt(self.gst_amount),
				})
			je.insert()
			self.db_set("advance_journal", je.name)	

def fetch_fuel_rate(hourly):
	match hourly:
		case "With Fuel (Internal)":
			return "with_fuel_internal"
		case "Without Fuel (Internal)":
			return "without_fuel_internal"
		case "Conifer - Cft (Internal)":
			return "conifer_internal"
		case "Broadleaf - Cft (Internal)":
			return "broadleaf_internal"
		case "With Fuel (External)":
			return "with_fuel_external"
		case "Without Fuel (External)":
			return "without_fuel_external"
		case "Conifer - Cft (External)":
			return "conifer_external"
		case "Broadleaf - Cft (External)":
			return "broadleaf_external"
		case _:
			return "Invalid option"

# def get_hire_rates(customer ="T-Customer" , equipment="EQUIP2400000", from_date= "18/11/2024"):
@frappe.whitelist()
def get_hire_rates(equipment_model, equipment_type, from_date, hourly):
		if not equipment_type or not equipment_model:
			frappe.throw("Equipment Details(Model/Type) are mandatory")
		
		hourly_name = fetch_fuel_rate(hourly)
		data = frappe.db.sql('''
							 select {hourly_name} as rate from `tabHire Charge Parameter` where equipment_model ='{equipment_model}' and equipment_type ='{equipment_type}';
							 '''.format(hourly_name=hourly_name,equipment_model=equipment_model, equipment_type=equipment_type),as_dict=True)
		if not data:
			frappe.throw(_("No Hire Rates has been assigned for equipment type {0} and model {1}").format(equipment_type, equipment_model), title="No Data Found!")
		return data	

@frappe.whitelist()
def get_idle_rates(equipment_model, equipment_type, from_date, idle_rate_type):
		if not equipment_type or not equipment_model:
			frappe.throw("Equipment Details(Model/Type) are mandatory")
		# e = frappe.get_doc("Equipment", equipment)
		idle_type = ""
		if idle_rate_type == "Internal":
			idle_type = "idle_internal"
		else:
			idle_type = "idle_external"
		data = frappe.db.sql('''
							 select {idle_rate_type} as idle_rate from `tabHire Charge Parameter` where equipment_model ='{equipment_model}' and equipment_type ='{equipment_type}';
							 '''.format(idle_rate_type=idle_type ,equipment_model=equipment_model, equipment_type=equipment_type),as_dict=True)
		if not data:
			frappe.throw(_("No Idle Rates has been assigned for equipment type {0} and model {1}").format(equipment_type, equipment_model), title="No Data Found!")
		return data		

@frappe.whitelist()
def get_diff_hire_rates(tr):
	query = "select with_fuel, without_fuel, idle_rate as idle from `tabTender Hire Rate` where name = \"" + str(tr) + "\""
	data = frappe.db.sql(query, as_dict=True)
	if not data:
		frappe.throw("No Hire Rates has been assigned")
	return data	

@frappe.whitelist()
def get_rates(form):
	if form:
		return frappe.db.sql('''select equipment, idle_rate, total_hours, rate_type, rate, from_date, to_date, from_time, to_time, tender_hire_rate from `tabHiring Approval Details` where docstatus = 1 and parent ='{form}';
							 '''.format(form=form),as_dict=True)

# @frappe.whitelist()
# def get_rates(form, equipment):
#     # Fetch rates using parameterized queries
#     query = """
#         SELECT rate_type, rate, idle_rate, from_date, to_date, from_time, to_time, place
#         FROM `tabHiring Approval Details`
#         WHERE name = %(form)s AND equipment = %(equipment)s
#     """
#     rates = frappe.db.sql(query, {"form": form, "equipment": equipment}, as_dict=True)
#     if rates:
#         return rates[0]
#     else:
#         frappe.throw(_("No rates found for the given Equipment and Hiring Form"))


# @frappe.whitelist()
# def update_status(name, customer, equipment):
# 	# Get the hire rates based on customer and equipment
#     hire_rates = get_hire_rates(customer, equipment)
# 	so = frappe.get_doc("Equipment Hiring Form", name)
# 	so.db_set("payment_completed", 1)

# 	# Additional code if you want to use `hire_rates` in some way
# 	frappe.msgprint(f"Hire rates fetched: {hire_rates}")
# def update_status(name):
# 	so = frappe.get_doc("Equipment Hiring Form", name)
# 	so.db_set("payment_completed", 1)

# @frappe.whitelist()
# def equipment_query(doctype, txt, searchfield, start, page_len, filters):
#     return frappe.db.sql("""
#                     select
#                             e.name,
#                             e.equipment_type,
#                             e.equipment_name
#                     from `tabEquipment` e
#                     where e.equipment_type = %(equipment_type)s
#                     and e.branch = %(branch)s
#                     and (
#                             {key} like %(txt)s
#                             or
#                             equipment_type like %(txt)s
#                             or
#                             equipment_name like %(txt)s
#                     )
#                     {mcond}
#                     order by
#                             if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
#                             if(locate(%(_txt)s, equipment_type), locate(%(_txt)s, equipment_type), 99999),
#                             if(locate(%(_txt)s, equipment_name), locate(%(_txt)s, equipment_name), 99999),
#                             idx desc,
#                             name, equipment_type, equipment_name
#                     limit %(start)s, %(page_len)s
#                     """.format(**{
#                             'key': searchfield,
#                             'mcond': get_match_cond(doctype)
#                     }),
#                     {
#                         "txt": "%%%s%%" % txt,
#                         "_txt": txt.replace("%", ""),
#                         "start": start,
#                         "page_len": page_len,
#                         "equipment_type": filters['equipment_type'],
#                         "branch": filters['branch']
#                     })

@frappe.whitelist()
def update_status(name):
	so = frappe.get_doc("Equipment Hiring Form", name)
	so.db_set("payment_completed", 1)

@frappe.whitelist()
def equipment_query(doctype, txt, searchfield, start, page_len, filters):
	# 	# Shiv, 20/12/2017
	# 	# Following code temporarily replaced by the subsequent as per Payma's request for doing backlog entries, 20/12/2017
	# 	# Needs to be set back later
	# 	'''
	# return frappe.db.sql("""
	# 					select
	# 							e.name,
	# 							e.equipment_type,
	# 							e.equipment_name
	# 					from `tabEquipment` e
	# 					where e.equipment_type = %s
	# 					and e.branch = %s
	# 					and e.is_disabled != 1
	# 					and e.not_cdcl = 0
	# 					and not exists (select 1
	# 									from `tabEquipment Reservation Entry` a
	# 									where (
	# 											a.from_date != a.to_date
	# 											and
	# 											(a.from_date between %s and %s or a.to_date between %s and %s)
	# 											)
	# 									and a.equipment = e.name)
	# 					""", (filters['equipment_type'], filters['branch'], filters['from_date'], filters['to_date'], filters['from_date'], filters['to_date']))
	# 	'''
		
	# 	# return frappe.db.sql("""
	# 	# 				select
	# 	# 						e.name,
	# 	# 						e.equipment_type,
	# 	# 						e.equipment_name
	# 	# 				from `tabEquipment` e
	# 	# 				where e.equipment_type = %(equipment_type)s
	# 	# 				and e.branch = %(branch)s
	# 	# 				and e.is_disabled != 1
	# 	# 				and (
	# 	# 						{key} like %(txt)s
	# 	# 						or
	# 	# 						equipment_type like %(txt)s
	# 	# 						or
	# 	# 						equipment_name like %(txt)s
	# 	# 				)
	# 	# 				{mcond}
	# 	# 				order by
	# 	# 						if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
	# 	# 						if(locate(%(_txt)s, equipment_type), locate(%(_txt)s, equipment_type), 99999),
	# 	# 						if(locate(%(_txt)s, equipment_name), locate(%(_txt)s, equipment_name), 99999),
	# 	# 						idx desc,
	# 	# 						name, equipment_type, equipment_name
	# 	# 				limit %(start)s, %(page_len)s
	# 	# 				""".format(**{
	# 	# 						'key': searchfield,
	# 	# 						'mcond': get_match_cond(doctype)
	# 	# 				}),
	# 	# 				{
	# 	# 		"txt": "%%%s%%" % txt,
	# 	# 		"_txt": txt.replace("%", ""),
	# 	# 		"start": start,
	# 	# 		"page_len": page_len,
	# 	# 						"equipment_type": filters['equipment_type'],
	# 	# 						"branch": filters['branch']
	# 	# 	})
		return frappe.db.sql("""
						select
								e.name,
								e.equipment_type,
								e.equipment_name
						from `tabEquipment` e
						where e.equipment_type = %(equipment_type)s
						and e.is_disabled != 1
						and e.not_cdcl = 0
						and (
								{key} like %(txt)s
								or
								equipment_type like %(txt)s
								or
								equipment_name like %(txt)s
						)
						{mcond}
						order by
								if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
								if(locate(%(_txt)s, equipment_type), locate(%(_txt)s, equipment_type), 99999),
								if(locate(%(_txt)s, equipment_name), locate(%(_txt)s, equipment_name), 99999),
								idx desc,
								name, equipment_type, equipment_name
						limit %(start)s, %(page_len)s
						""".format(**{
								'key': searchfield,
								'mcond': get_match_cond(doctype)
						}),
						{
				"txt": "%%%s%%" % txt,
				"_txt": txt.replace("%", ""),
				"start": start,
				"page_len": page_len,
				"equipment_type": filters['equipment_type']
			})

@frappe.whitelist()        
def get_advance_balance(branch, customer):	
	if branch and customer:
		data = []
		query = "select e.name as journal, a.name as name, a.credit as amount, a.party as party, \
		a.reference_type as ref_type, \
			a.reference_name as ref_name, a.cost_center as cc, e.posting_date as \
			posting_date from `tabJournal Entry` as e, `tabJournal Entry Account` as a \
			where e.name = a.parent and e.branch = \'" + str(branch) + "\' and e.docstatus = '1' and a.party = \'" + str(customer) + "\' \
			and a.reference_type='Equipment Hiring Form'"
		for a in frappe.db.sql(query, as_dict=True):
			# frappe.throw(_(" Test : {0}".format(a.amount)))
			# row = [a.name, a.amount, a.party, a.ref_type, a.ref_name, a.cc]
			ehform = frappe.db.sql("SELECT docstatus, payment_completed FROM `tabEquipment Hiring Form` \
				WHERE name = \'"+ str(a.ref_name) +"\'", as_dict=True)
			if ehform[0]['docstatus'] == 1 and ehform[0]['payment_completed'] == 1:
				invoicecharge = frappe.db.sql("SELECT  count(*) as count \
					FROM `tabHire Invoice Advance` as a \
					INNER JOIN `tabHire Charge Invoice` as c on a.parent=c.name \
					INNER JOIN `tabEquipment Hiring Form` as eq on c.ehf_name = eq.name \
					WHERE a.reference_row = \'" + str(a.name) + "\' \
					and eq.docstatus = '1' and eq.payment_completed = '1'", as_dict=True);
				if invoicecharge[0]['count'] < 1:
					data.append({"journal":a.journal, "name":a.name, "amount":a.amount, "party":a.party, "ref_type":a.ref_type, "ref_name":a.ref_name, "cost_center":a.cc, "posting_date":a.posting_date})
		return data
	else:
		frappe.throw("Select Equipment Hiring Form first!")	



@frappe.whitelist()
def make_vehicle_logbook(source_name, target_doc=None): 
	def update_docs(obj, target, source_parent):
		# frappe.throw(str(target))
		target.posting_date = nowdate()
		target.payment_for = "Equipment Hiring Form"
		target.net_amount = obj.advance_amount
		target.actual_amount = obj.advance_amount
		target.income_account = frappe.db.get_value("Branch", obj.branch, "revenue_bank_account")
	
		target.append("items", {
			"reference_type": "Equipment Hiring Form",
			"reference_name": obj.name,
			"outstanding_amount": obj.advance_amount,
			"allocated_amount": obj.advance_amount,
			"customer": obj.customer
		})

	doc = get_mapped_doc("Equipment Hiring Form", source_name, {
			"Equipment Hiring Form": {
				"doctype": "Vehicle Logbook",
				"field_map": {
					"outstanding_amount": "receivable_amount",
				},
				"postprocess": update_docs,
				"validation": {"docstatus": ["=", 1], "equipment_hiring_form": ["is", None]}
			},
		}, target_doc)
	return doc
