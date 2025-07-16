# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import (
	add_days,
	add_months,
	cint,
	date_diff,
	flt,
	get_datetime,
	get_last_day,
	get_first_day,
	getdate,
	month_diff,
	nowdate,
	today,
	get_year_ending,
	get_year_start,
	formatdate,
)
from frappe.utils import flt, formatdate, get_link_to_form, getdate

from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_checks_for_pl_and_bs_accounts,
)
from erpnext.assets.doctype.asset.asset import get_asset_value_after_depreciation
from erpnext.assets.doctype.asset.depreciation import get_depreciation_accounts
from erpnext.assets.doctype.asset_activity.asset_activity import add_asset_activity
from erpnext.assets.doctype.asset_depreciation_schedule.asset_depreciation_schedule import (
	make_new_active_asset_depr_schedules_and_cancel_current_ones,
)
from erpnext.accounts.accounts_custom_functions import get_number_of_days
from erpnext.accounts.accounts_custom_functions import update_jv, update_de

class AssetValueAdjustment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		asset: DF.Link
		asset_category: DF.ReadOnly | None
		asset_name: DF.Data | None
		branch: DF.Link | None
		company: DF.Link | None
		cost_center: DF.Link | None
		credit_account: DF.Link
		current_asset_value: DF.Currency
		date: DF.Date
		difference_amount: DF.Currency
		finance_book: DF.Link | None
		fixed_asset_account: DF.Link
		journal_entry: DF.Link | None
		new_asset_value: DF.Currency
		re_valued: DF.Check
	# end: auto-generated types

	def validate(self):
		self.validate_date()
		self.set_current_asset_value()
		# self.set_difference_amount()
		self.set_new_asset_value()

	def on_submit(self):
		# self.make_depreciation_entry()
		# self.update_asset(self.new_asset_value)
		# add_asset_activity(
		# 	self.asset,
		# 	_("Asset's value adjusted after submission of Asset Value Adjustment {0}").format(
		# 		get_link_to_form("Asset Value Adjustment", self.name)
		# 	),
		# )
		self.change_value(self.new_asset_value)
		self.update_asset()

	def on_cancel(self):
		doc = frappe.get_doc("Journal Entry", self.journal_entry)
		doc.cancel()
		self.update_asset(self.current_asset_value)
		self.remove_adjustment_value()
		add_asset_activity(
			self.asset,
			_("Asset's value adjusted after cancellation of Asset Value Adjustment {0}").format(
				get_link_to_form("Asset Value Adjustment", self.name)
			),
		)

	def remove_adjustment_value(self):
		doc = frappe.get_doc("Asset", self.asset)
		doc.db_set("additional_value", doc.additional_value - self.difference_amount)
	
	def validate_date(self):
		asset_purchase_date = frappe.db.get_value("Asset", self.asset, "purchase_date")
		if getdate(self.date) < getdate(asset_purchase_date):
			frappe.throw(
				_("Asset Value Adjustment cannot be posted before Asset's purchase date <b>{0}</b>.").format(
					formatdate(asset_purchase_date)
				),
				title=_("Incorrect Date"),
			)

	# def set_difference_amount(self):
	# 	self.difference_amount = flt(self.current_asset_value - self.new_asset_value)

	def set_new_asset_value(self):
		self.new_asset_value = flt(self.current_asset_value + self.difference_amount)

	def set_current_asset_value(self):
		if not self.current_asset_value and self.asset:
			self.current_asset_value = get_asset_value_after_depreciation(self.asset, self.finance_book)

	def make_depreciation_entry(self):
		# asset = frappe.get_doc("Asset", self.asset)
		# (
		# 	_,
		# 	accumulated_depreciation_account,
		# 	depreciation_expense_account,
		# ) = get_depreciation_accounts(asset.asset_category, asset.company)

		# depreciation_cost_center, depreciation_series = frappe.get_cached_value(
		# 	"Company", asset.company, ["depreciation_cost_center", "series_for_depreciation_entry"]
		# )
		# depreciation_cost_center, depreciation_series = frappe.get_cached_value(
		# 	"Company", asset.company, ["depreciation_cost_center", "series_for_depreciation_entry"]
		# )
		# depreciation_series = depreciation_series or "DEP-.YYYY.-"  # Default fallback series


		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.naming_series = "Journal Entry"
		je.posting_date = self.date
		je.company = self.company
		je.remark = f"Asset Adjustment Entry against {self.asset} worth {self.difference_amount}"
		je.finance_book = self.finance_book
		je.branch = self.branch

		credit_entry = {
			"account": self.credit_account,
			"credit_in_account_currency": self.difference_amount,
			"cost_center": self.cost_center,
			"reference_type": "Asset",
			"reference_name": self.asset,
		}

		debit_entry = {
			"account": self.fixed_asset_account,
			"debit_in_account_currency": self.difference_amount,
			"cost_center": self.cost_center,
			"reference_type": "Asset",
			"reference_name": self.asset,
		}

		accounting_dimensions = get_checks_for_pl_and_bs_accounts()

		for dimension in accounting_dimensions:
			if dimension.get("mandatory_for_bs"):
				credit_entry.update(
					{
						dimension["fieldname"]: self.get(dimension["fieldname"])
						or dimension.get("default_dimension")
					}
				)

			if dimension.get("mandatory_for_pl"):
				debit_entry.update(
					{
						dimension["fieldname"]: self.get(dimension["fieldname"])
						or dimension.get("default_dimension")
					}
				)

		je.append("accounts", credit_entry)
		je.append("accounts", debit_entry)

		je.flags.ignore_permissions = True
		je.submit()

		self.db_set("journal_entry", je.name)
		doc = frappe.get_doc("Asset", self.asset)
		doc.db_set("additional_value", self.difference_amount)

	def change_value(self, values):	
		asset= self.asset
		value = flt(self.difference_amount)
		start_date = self.date
		credit_account = self.credit_account
		asset_account = self.fixed_asset_account
		
		if(asset and value and getdate(start_date) <= getdate(nowdate())):   
			asset_obj = frappe.get_doc("Asset", asset)

			if asset_obj and asset_obj.docstatus == 1:
				value = -1*flt(value) if self.docstatus == 2 else flt(value)
				#Make GL Entries for additional values and update gross_amount (rate)
				asset_obj.db_set("additional_value", flt(asset_obj.additional_value) + flt(value))
				asset_obj.db_set("gross_purchase_amount", flt(flt(asset_obj.gross_purchase_amount) + flt(value)))
				if self.docstatus == 1:
					self.make_gl_entry(asset_account, credit_account, value, asset_obj, start_date)
				#Get dep. schedules which had not yet happened
				asset_depreciation_schedule = frappe.db.get_value(
					"Asset Depreciation Schedule",
					filters={"asset": asset_obj.name, "docstatus": 1},
					fieldname="name"
					)
				# asset_depreciation_schedule = frappe.db.get_value("Asset Depreciation Schedule",filters:{"asset":asset_obj.name,"docstatus":1},fields={"name"})
				# frappe.throw(str(asset_depreciation_schedule))
				schedules = frappe.db.get_all("Depreciation Schedule", order_by="schedule_date", filters = {"parent": asset_depreciation_schedule, "schedule_date": [">=", start_date]},fields={"name", "schedule_date", "journal_entry",  "depreciation_amount", "accumulated_depreciation_amount", "income_depreciation_amount","income_accumulated_depreciation"})

				# frappe.throw(frappe.as_json(schedules))
				##Get total number of dep days for the asset
				total_days = get_number_of_days(add_days(getdate(start_date), -1), schedules[-1]['schedule_date'])
				##Assign the last dep schedule date for num of days calc
				asset_depreciation_percent = asset_obj.get('finance_books')[0].income_depreciation_percent
				last_sch_date = add_days(getdate(start_date), -1)
				for i in schedules:
					#Add additional values to the depreciation schedules
					#Calc num of days for each dep schedule
					num_days = get_number_of_days(last_sch_date, i.schedule_date)
					#Calc num of days till current schedule
					num_till_days = get_number_of_days(start_date, i.schedule_date)
					##Updated dep amount
					dep_amount = flt(i.depreciation_amount) + (flt(value) * num_days / total_days)
					##Updated accu dep amount
					accu_dep = flt(i.accumulated_depreciation_amount) + (flt(value) * num_till_days / total_days)
					#Income amount
					income = flt(i.income_depreciation_amount) + (flt(value)/(100 * 365.25)) * flt(asset_depreciation_percent) * num_days
					#Accumulated Income amount
					accu_income = flt(i.income_accumulated_depreciation) + (flt(value)/(100 * 365.25)) * flt(asset_depreciation_percent) * num_till_days
					self.update_value(i.name, dep_amount, accu_dep, income, accu_income)
					if i.journal_entry:
						update_jv(i.journal_entry, dep_amount)
					if i.depreciation_entry:
						update_de(i.depreciation_entry, dep_amount, asset)

					##Update last dep schedule date
					last_sch_date = i.schedule_date

				#Add the reappropriation details for record
				# app_details = frappe.new_doc("Asset Modification Entries")
				# app_details.flags.ignore_permissions=1
				# app_details.asset = asset
				# app_details.value = value
				# app_details.credit_account = credit_account
				# app_details.asset_account = asset_account
				# app_details.addition_date = start_date
				# app_details.posted_on = nowdate()
				# app_details.submit()
				return "DONE"
			elif asset_obj.docstatus == 2:
				return "Cannot add value to CANCELLED assets"
			else:
				return "Invalid asset code"
		elif not asset:
			frappe.throw("Invalid asset code")

		elif not value:
			frappe.throw("Invalid asset value")
		elif start_date > nowdate():
			frappe.throw("Effective Date cannot be greater than Today")
		else:
			frappe.throw("Sorry, something happened. Please try again")

	def make_gl_entry(self, asset_account, credit_account, value, asset, start_date):
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1

		je.update({
			"voucher_type": "Journal Entry",
			"company": asset.company,
			"remark": "Value (" + str(value) +" ) added to " + asset.name + " (" + asset.asset_name + ") ",
			"user_remark": "Value (" + str(value) +" ) added to " + asset.name + " (" + asset.asset_name + ") ",
			"posting_date": start_date,
			"branch": asset.branch,
			"naming_series":'Journal Entry'
			})

		#credit account update
		party = party_type = None
		account_type = frappe.db.get_value("Account", credit_account, "account_type") or ""
		if account_type in ["Receivable", "Payable"]:
			party = self.party
			party_type = self.party_type
		je.append("accounts", {
			"account": credit_account,
			"party":party,
			"party_type":party_type,
			"credit_in_account_currency": flt(value),
			"reference_type": "Asset Value Adjustment",
			"reference_name": self.name,
			"cost_center": asset.cost_center,
			# "business_activity": asset.business_activity,
			})

		#debit account update
		je.append("accounts", {
			"account": asset_account,
			"debit_in_account_currency": flt(value),
			"reference_type": "Asset Value Adjustment",
			"reference_name": self.name,
			"cost_center": asset.cost_center,
			# "business_activity": asset.business_activity,
			})
		je.flags.ignore_permissions=1
		je.submit()
		self.db_set("journal_entry", je.name)

	def update_value(self, sch_name, dep_amount, accu_dep, income, accu_income):
		sch = frappe.get_doc("Depreciation Schedule", sch_name)
		sch.db_set("depreciation_amount",dep_amount)
		sch.db_set("accumulated_depreciation_amount", accu_dep)
		sch.db_set("income_depreciation_amount", income)
		sch.db_set("income_accumulated_depreciation", accu_income)
		
	def update_asset(self, cancel=False):
		if self.re_valued:
			if cancel:
				frappe.db.set_value("Asset",self.asset,"revalued_asset_value", 0)
				frappe.db.set_value("Asset",self.asset, "re_valued", 0)
			else:
				frappe.db.set_value("Asset",self.asset,"revalued_asset_value", self.new_asset_value)
				frappe.db.set_value("Asset",self.asset,"re_valued", 1)
	# def update_asset(self, asset_value):
	# 	asset = frappe.get_doc("Asset", self.asset)

	# 	if not asset.calculate_depreciation:
	# 		asset.value_after_depreciation = asset_value
	# 		asset.save()
	# 		return

	# 	asset.flags.decrease_in_asset_value_due_to_value_adjustment = True

	# 	if self.docstatus == 1:
	# 		notes = _(
	# 			"This schedule was created when Asset {0} was adjusted through Asset Value Adjustment {1}."
	# 		).format(
	# 			get_link_to_form("Asset", asset.name),
	# 			get_link_to_form(self.get("doctype"), self.get("name")),
	# 		)
	# 	elif self.docstatus == 2:
	# 		notes = _(
	# 			"This schedule was created when Asset {0}'s Asset Value Adjustment {1} was cancelled."
	# 		).format(
	# 			get_link_to_form("Asset", asset.name),
	# 			get_link_to_form(self.get("doctype"), self.get("name")),
	# 		)

	# 	make_new_active_asset_depr_schedules_and_cancel_current_ones(
	# 		asset, notes, value_after_depreciation=asset_value, ignore_booked_entry=True
	# 	)
	# 	asset.flags.ignore_validate_update_after_submit = True
	# 	asset.save()

	@frappe.whitelist()
	def update_def_account(self):
		if self.re_valued:
			account= "Revaluation Income/(Loss) - SMCL"
		else:
			account = " "
		return account