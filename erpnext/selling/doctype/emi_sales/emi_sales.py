# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, get_first_day, cint
from erpnext.controllers.selling_controller import SellingController
from erpnext.accounts.utils import get_account_currency
from frappe.utils import cint, flt, add_months, today, date_diff, getdate, add_days, cstr, nowdate, month_diff
from frappe.utils.data import get_first_day, get_last_day, add_years
from frappe import _
# from erpnext.selling.doctype.commission.commission import get_commission_taxable_tds_percent
from erpnext.production.doctype.selling_price.selling_price import get_selling_rate
# from erpnext.selling.selling_utils import nofity_hr
from erpnext.custom_utils import check_budget_available, cancel_budget_entry, check_future_date
# from erpnext.selling.doctype.commission.commission import get_commission_taxable_tds_percent
import math

class EMISales(SellingController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.selling.doctype.emi_payment_schedule.emi_payment_schedule import EMIPaymentSchedule
		from erpnext.selling.doctype.emi_sales_installments.emi_sales_installments import EMISalesInstallments
		from erpnext.selling.doctype.emi_sales_item.emi_sales_item import EMISalesItem
		from erpnext.selling.doctype.emi_sales_payment_mode.emi_sales_payment_mode import EMISalesPaymentMode
		from frappe.types import DF

		address: DF.Data | None
		air_time: DF.Check
		amended_from: DF.Link | None
		apply_purchase_limit: DF.Check
		asset_code: DF.Link | None
		base_paid_amount: DF.Currency
		billing_user: DF.Data | None
		branch: DF.Link
		business_activity: DF.Link | None
		cid_passort_work_permit_no: DF.Data | None
		collection_center: DF.Data | None
		commission_amount: DF.Currency
		company: DF.Link | None
		contact: DF.Data | None
		conversion_rate: DF.Float
		cost_center: DF.Link | None
		cost_sharing_percentage: DF.Percent
		credit_type: DF.Literal["", "Installment Payment", "Due Date Payment"]
		currency: DF.Link | None
		customer: DF.DynamicLink
		customer_email: DF.Data | None
		customer_group: DF.Link
		customer_name: DF.Data | None
		customer_type: DF.Literal["Customer", "Employee"]
		debit_to: DF.Link | None
		delivery_warehouse: DF.Link
		discount_amount: DF.Currency
		down_payment: DF.Check
		down_payment_amount: DF.Currency
		due_date: DF.Date | None
		email_address: DF.Data | None
		grand_total: DF.Currency
		installment_details: DF.Table[EMISalesInstallments]
		interest_percentage: DF.Percent
		is_discounted: DF.Check
		is_existing: DF.Check
		is_on_credit: DF.Check
		is_opening_bal: DF.Check
		is_return: DF.Check
		items: DF.Table[EMISalesItem]
		location_segregation: DF.Data | None
		mode_of_payment_items: DF.Table[EMISalesPaymentMode]
		monthly_deduction: DF.Currency
		net_amount: DF.Currency
		no_of_installation: DF.Literal["", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
		no_of_installation_employee: DF.Literal["", "1", "2", "3", "4", "5"]
		no_of_installation_external: DF.Literal["", "1", "2", "3", "4", "5", "6", "7"]
		no_of_installments_paid: DF.Int
		one_time_customer_name: DF.Data | None
		outstanding_amount: DF.Currency
		paid_amount: DF.Currency
		payment_schedule: DF.Table[EMIPaymentSchedule]
		payment_type: DF.Link | None
		posting_date: DF.Date
		posting_time: DF.Time | None
		pricing_date: DF.Date | None
		profit_center: DF.Data | None
		purchase_limit_on_total_amount: DF.Currency
		recalculate_amortization: DF.Check
		recovery_end_date: DF.Date | None
		recovery_start_date: DF.Date | None
		remarks: DF.SmallText | None
		required_commission: DF.Check
		salary_component: DF.Link | None
		salary_structure: DF.Link | None
		sales_order_type: DF.Link
		set_price_date_manually: DF.Check
		status: DF.Data | None
		taxable_amount: DF.Currency
		taxes_and_charges: DF.Float
		tds_amount: DF.Currency
		total_interest_amount: DF.Currency
		total_receivable_amount: DF.Currency
		total_tds_amount: DF.Currency
		total_tds_deducted_by_customer: DF.Currency
	# end: auto-generated types
	def validate(self):
		# self.validate_sales_user()
		self.update_table()
		self.validate_mandatory()
		check_future_date(self.posting_date)
		self.validate_data()
		self.validate_uom_is_integer("stock_uom", "stock_qty")
		self.validate_uom_is_integer("uom", "qty")
		# self.restrict_employee_purchase()
		self.get_customer_details()
		self.calculate_amount()
		self.set_status()
		self.validate_serial_number()
		# self.validate_mode_of_payment()
		self.update_recovery_details()
		self.create_payment_schedule()
		self.check_mode_of_payment_amount()
		# self.check_daily_collection()

	def on_submit(self):
		# frappe.throw("here")
		# self.check_purchase_limit()
		self.check_mode_of_payment_amount()
		self.update_stock_ledger()
		self.update_salary_structure()
		self.make_gl_entries()
		self.post_gl_for_payment()
		# self.capitalize_material()
		# self.set_status()
		# if self.customer_type == 'Employee':
		# 	nofity_hr(self.doctype,self.name)
		# self.consume_budget()

	def on_cancel(self):
		self.calculate_amount()
		self.update_stock_ledger()
		self.make_gl_entries_on_cancel()
		self.update_salary_structure(True)
		# self.cancel_budget() commented as commission not required for STCBL

	def on_update_after_submit(self):
		# frappe.throw("here")
		user = frappe.session.user
		user_roles = frappe.get_roles(user)
		# if "Sales Editor" not in user_roles and self.docstatus == 1:
		# 	frappe.throw("Only users with role <b>Sales Editor</b> are allowed to edit submitted documents.")

	def validate_sales_user(self):
		if not frappe.db.exists('User Mapping',{"user": frappe.session.user}):
			if frappe.session.user != "Administrator":
				frappe.throw('Your email id is not mapped to any billing user.', title="Cannot Create Sales Order")

	def validate_serial_number(self):
		count = 1
		for a in self.items:
			if len(str(a.serial_number)) not in  (16,6) and a.item_subgroup == 'Voucher':
				frappe.throw("From Serial Number should be 16 or 6 digits long in table at row {}".format(str(count)))
			if a.actual_qty > 1 and a.item_subgroup == 'Voucher':
				if len(str(a.to_serial_number)) not in  (16,6):
					frappe.throw("To Serial Number should be 16 or 6 digits long in table at row {}".format(str(count)))
				if (flt(a.to_serial_number) - flt(a.serial_number))+1 != a.qty:
					frappe.throw("Range between From Serial Number and To Serial Number does not match with quantity in table at row {}".format(str(count)))
			count += 1

	# def capitalize_material(self):
	# 	if self.sales_order_type == "Cost Sharing Installment":
	# 		self.update_asset_from_old_code_base()

	@frappe.whitelist()
	def get_asset_details(self):
		exists = 0
		if frappe.db.exists("Asset Issue Details", {"emi_sales":self.name, "docstatus": ["<", 2]}):
			exists = 1
			frappe.throw("Asset Issue Details for this EMI Sales already exists.")

		cost_sharing_quotaamount = frappe.db.get_value("Employee Grade", frappe.db.get_value("Employee", self.customer, "grade"), "cost_sharing_quotaamount")

		for item in self.items:
			# ae.flags.ignore_permissions = 1
			# ae.item_code = a.item_code
			# # ae.brand = a.brand
			# # ae.model = a.model
			# ae.child_ref = a.name
			# ae.item_name = a.item_name
			# ae.qty = int(b)
			# #ae.company = self.company
			# ae.received_date = self.posting_date
			# ae.reference_type = "EMI Sales"
			# ae.ref_doc = self.name
			ae = frappe.new_doc("Asset Received Entries")
			ae.flags.ignore_permissions = 1
			ae.item_code = item.item_code
			# ae.brand = a.brand
			# ae.model = a.model
			ae.child_ref = item.name
			ae.item_name = item.item_name
			ae.qty = int(item.qty)
			#ae.company = self.company
			ae.received_date = self.posting_date
			ae.reference_type = "EMI Sales"
			ae.ref_doc = self.name
			ae.branch = frappe.db.get_value("Branch",{"cost_center":self.cost_center},"name")
			#ae.branch = frappe.db.get_value("Cost Center", a.cost_center, "branch")
			ae.submit()
			branch = frappe.db.get_value("Branch",{"cost_center":self.cost_center},"name")
			asset_rate = flt(flt(cost_sharing_quotaamount)/2,2)
			item_code = item.item_code
			item_name = item.item_name
			asset_category = frappe.db.get_value("Item", item.item_code, "asset_category")
			asset_sub_category = frappe.db.get_value("Item", item.item_code, "asset_sub_category")
			fixed_asset_account, credit_account=frappe.db.get_value("Asset Category Account", {'parent':asset_category}, ['fixed_asset_account','credit_account'])
			next_depreciation_date = get_last_day(self.posting_date)
			#ae.branch = frappe.db.get_value("Cost Center", a.cost_center, "branch")
			# ae.submit()
			# asset_code = self.create_asset(a.item_code, a.business_activity)
			# if count == 0:
			# 	asset_codes += str(asset_code)
			# else:
			# 	asset_codes += " ,"+str(asset_code)

			# count+=1
			return branch, asset_rate, item_code, item_name, asset_category, asset_sub_category, fixed_asset_account, credit_account, next_depreciation_date, exists

	def create_asset(self, item_code, business_activity):
		cost_sharing_quotaamount = frappe.db.get_value("Employee Grade", frappe.db.get_value("Employee", self.customer, "grade"), "cost_sharing_quotaamount")
		item_doc = frappe.get_doc("Item",item_code)
		employee_grade_quota_amt = frappe.db.get_value("Employee Grade", frappe.db.get_value("Employee", self.customer, "grade"), "cost_sharing_quotaamount")
		if item_doc.asset_category:
			asset_category = frappe.db.get_value("Asset Category", item_doc.asset_category, "name")
			fixed_asset_account, credit_account=frappe.db.get_value("Asset Category Account", {'parent':asset_category}, ['fixed_asset_account','credit_account'])
			if item_doc.asset_sub_category:
				for a in frappe.db.sql("select total_number_of_depreciations, income_depreciation_percent from `tabAsset Finance Book` where parent = '{0}' and asset_sub_category = '{1}'".format(asset_category, item_doc.asset_sub_category), as_dict=1):
					total_number_of_depreciations = a.total_number_of_depreciations
					depreciation_percent = a.income_depreciation_percent
			else:
				frappe.throw(_("No Asset Sub-Category for Item: " +"{}").format(item_doc.item_name))
		else:
			frappe.throw(_("<b>Asset Category</b> is missing for material {}").format(frappe.get_desk_link("Item", item_code)))
		
		asset = frappe.new_doc("Asset")
		# cost_center = frappe.db.get_value("Branch", self.branch, "cost_center")
		asset_category = frappe.db.get_value("Item", item_code, "asset_category")
		asset_sub_category = frappe.db.get_value("Item", item_code, "asset_sub_category")
		asset.item_code = item_code
		asset.asset_name = item_doc.item_name 
		asset.cost_center = self.cost_center
		asset.asset_category = asset_category
		asset.asset_sub_category = asset_sub_category
		asset.branch = self.branch
		asset.purchase_date = self.posting_date
		asset.next_depreciation_date = get_last_day(self.posting_date)
		asset.credit_account = credit_account
		asset.asset_account = fixed_asset_account
		asset.calculate_depreciation = 1
		asset.issued_to = self.customer
		asset.brand = item_doc.brand
		asset.model = item_doc.model
		# asset.serial_number = serial_no
		asset.asset_quantity_ = 1
		asset.asset_rate = flt(flt(cost_sharing_quotaamount)/2,2)
		asset.purchase_amount = flt(flt(cost_sharing_quotaamount)/2,2)
		asset.available_for_use_date = self.posting_date
		asset.business_activity = business_activity
		asset.company = self.company
		asset.gross_purchase_amount = flt(flt(cost_sharing_quotaamount)/2,2)
		asset.total_number_of_depreciations = total_number_of_depreciations
		asset.asset_depreciation_percent = depreciation_percent
		asset.stock_entry = self.name
		# asset.location = self.location
		asset.insert()
		asset.submit()
		asset_code = asset.name
		
		if asset_code:
			return asset_code
			# asset.submit()
		else:
			frappe.throw("Asset not able to create for asset issue no.".format(self.name))

	@frappe.whitelist()
	def check_balance(self):
		# balance = 0
		# data_balance = 0
		# for item in self.items:
		# 	balance += item.rate * item.qty
		# 	data_balance += item.total_data_package
		sales_editor = 0
		show_emi_button = 0
		show_full_payment_button = 9
		remaining_installment = 0
		if self.outstanding_amount > 0:
			show_emi_button = 1
			# if flt(self.outstanding_amount/self.monthly_deduction) >= 2:
			# 	show_full_payment_button = 1
			remaining_installment = flt(self.outstanding_amount/self.monthly_deduction,0)
		user_roles = frappe.get_roles(frappe.session.user)
		if "Sales Editor" in user_roles:
			sales_editor = 1
		
		return show_emi_button, show_full_payment_button, remaining_installment, sales_editor

		
			

	def update_table(self):
		for a in self.items:
			income_acc, exp_acc = frappe.db.get_value("Item Default",{"parent":a.item_code},["income_account","expense_account"])
			a.income_account = income_acc
			a.expense_account = exp_acc
			default_expense_account, default_receiveable_account, default_cash_account = frappe.db.get_value("Company", self.company, ["default_expense_account","default_receivable_account", "default_cash_account"])
			if a.item_group != "Trading Goods":
				a.expense_account = default_expense_account
			if self.is_on_credit == 1 or self.is_opening_bal == 1:
				a.cash_bank_account = default_receiveable_account
			else:
				a.cash_bank_account = default_cash_account
			# if self.required_commission == 1:
			# 	a.commission_account = frappe.db.get_single_value("Selling Settings", "default_commission_account")
			actual_qty = frappe.db.sql("""select actual_qty from `tabBin`
				where item_code = %s and warehouse = %s""", (a.item_code, self.delivery_warehouse))
			actual_qty = actual_qty and flt(actual_qty[0][0]) or 0
			a.actual_qty = flt(actual_qty)

	def validate_mandatory(self):
		row = 1
		if self.customer_type == "Customer" and self.payment_type == "External Customers Installment" and not self.no_of_installation_external:
			frappe.throw("No of Installation In Years(External Customers) is mandatory")
		for a in self.items:
			missing = []
			if not a.income_account:
				missing.append("Income Account")
			if not a.cash_bank_account:
				missing.append("Cash/Bank Account")
			if not a.expense_account:
				missing.append("Expense Account")
			# if self.required_commission == 1:
			# 	if not a.commission_account:
			# 		missing.append("Commission Account")
			if len(missing) != 0:
				frappe.throw("{} missing in row {} of Items table.".format(", ".join(b for b in missing), row))
			row += 1
	@frappe.whitelist()
	def post_accounting_entry(self):
		user_roles = frappe.get_roles(frappe.session.user)
		cash_bank_account = ''
		if flt(self.net_amount) <= 0:
			frappe.msgprint(title='Message',msg='Accounting Entry not required for this transaction as net amount is 0')
			return
		if self.is_on_credit or cint(self.is_opening_bal) == 1:
			cash_bank_account =  frappe.db.get_value('Company',self.company,'default_receivable_account')
		else:
			cash_bank_account =  frappe.db.get_value('Company',self.company,'default_cash_account')
		if frappe.db.exists('GL Entry',{'account':cash_bank_account,'voucher_no':self.name,'voucher_type':self.doctype}):
			frappe.msgprint(title='Message',msg="Accounting Enteris are already booked for this document")
		elif frappe.session.user != self.owner:
			if "Revenue Officer" not in user_roles:
				frappe.msgprint(title='Message',msg="Only document owner or RO can post accounting entry for this document",)
			else:
				self.post_gl_for_payment()
				if frappe.db.exists('GL Entry',{'account':cash_bank_account,'voucher_no':self.name,'voucher_type':self.doctype}):
					frappe.msgprint(title='Message',msg="Accounting Enteries posted for this document")
				else:
					frappe.msgprint(title='Message',msg="Accounting Enteries didn't post for this document, try again")
		else:
			self.post_gl_for_payment()
			if frappe.db.exists('GL Entry',{'account':cash_bank_account,'voucher_no':self.name,'voucher_type':self.doctype}):
				frappe.msgprint(title='Message',msg="Accounting Enteries posted for this document")
			else:
				frappe.msgprint(title='Message',msg="Accounting Enteries didn't post for this document, try again")

	def validate_data(self):
		if cint(self.is_opening_bal) == 1 and self.sales_order_type != 'Opening Sales':
			frappe.throw(title='Message',msg='Sales order type must be <b>Opening Sales</b> for opening entry')
		if not self.cost_center:
			self.cost_center = frappe.db.get_value('Branch',self.branch,'cost_center')
		if self.customer_type == "Employee" and self.sales_order_type == "External Customers":
			frappe.throw("External Customers not applicable for customer type Employee")
		if not self.cost_center:
			frappe.throw('Cost Center is mandatory')
		if self.credit_type == 'Installment Payment' and self.payment_type not in ['External Customers Installment','Staff Installment','Employee Installment','Cost Sharing Installment']:
			frappe.throw(title='Message',msg='For <b>{credit_type}</b>, Payment Type should not be {payment_type}'.format(credit_type=self.credit_type,payment_type=self.payment_type))
	def check_mode_of_payment_amount(self):
		total = 0
		for p in self.mode_of_payment_items:
			if flt(p.amount) != flt(self.grand_total) and self.payment_type in ("External Customers Installment", "Staff Installment", "Employee Installment", "Cost Sharing Installment"):
				p.amount = flt(self.grand_total)
			total += flt(p.amount)
			if self.is_on_credit and p.mode_of_payment != 'Credit':
				frappe.throw(title='Message',
					msg='Mode of payment cannot be <b>{}</b> for Credit Sale'.format(p.mode_of_payment))
			if cint(self.is_opening_bal) == 1 and p.mode_of_payment != 'Credit':
				frappe.throw(title='Message',
					msg='Mode of payment cannot be <b>{}</b> for Opening Sale'.format(p.mode_of_payment))

		if flt(total,2) != flt(self.net_amount,2):
			if self.payment_type not in ("External Customers", "Staff Installment", "Employee Installment", "Cost Sharing Installment"):
				frappe.throw('Sum of amount collected in different mode of payment must be equal to net amount of <b>{}</b>'.format(self.net_amount))

	def check_daily_collection(self):
		if frappe.db.exists('Daily Collection',{'user_id':frappe.session.user,'transaction_date':self.posting_date,'docstatus':1}):
			frappe.throw(title='Error',msg='You have already created Daily Collection for date <b>{0}</b>.To proceed with transaction you have to cancel your daily of date {0}'.format(self.posting_date))
	def restrict_employee_purchase(self):
		if self.customer_type == 'Customer':
			return
		qty = 0
		for item in self.items:
			if frappe.db.exists('Items Allowed For Employee',{'item_sub_group':item.item_subgroup}):
				prev_bought = frappe.db.sql('''
							SELECT sum(i.qty) as qty 
								FROM `tabEMI Sales` b INNER JOIN `tabEMI Sales Item` i ON i.parent = b.name
							WHERE b.customer = '{}' AND b.docstatus = 1 AND b.posting_date >= '{}' AND b.posting_date <= '{}'
							AND i.item_subgroup = '{}' and b.sales_order_type = '{}'
						'''.format(self.customer,frappe.defaults.get_user_default("year_start_date"),frappe.defaults.get_user_default("year_end_date"),item.item_subgroup, self.sales_order_type))[0][0]
				if self.sales_order_type != 'Employee Installment':
					if flt(prev_bought) + flt(item.qty) > flt(frappe.db.get_value('Items Allowed For Employee',{'item_sub_group':item.item_subgroup},'qty')):
						frappe.throw(title='Error',msg='Employee {} cannot purchase item {} from EMI Sales more than {} {}'.format(self.customer,item.item_name,frappe.db.get_value('Items Allowed For Employee',{'item_sub_group':item.item_subgroup},'qty'),item.uom))
				else:
					if flt(prev_bought) + flt(item.qty) > flt(frappe.db.get_value('Items Allowed For Employee',{'item_sub_group':item.item_subgroup},'qty'))+2:
						frappe.throw(title='Error',msg='Employee {} cannot purchase item {} from EMI Sales more than {} {}'.format(self.customer,item.item_name,frappe.db.get_value('Items Allowed For Employee',{'item_sub_group':item.item_subgroup},'qty')+2,item.uom))
			else:
				frappe.throw('Employee {} is not allowed to purchase item {} from EMI Sales'.format(self.customer,item.item_name))
			qty += flt(item.qty)
		prev_qty = frappe.db.sql('''
			SELECT sum(i.qty) as qty 
				FROM `tabEMI Sales` b INNER JOIN `tabEMI Sales Item` i ON i.parent = b.name
			WHERE b.customer = '{}' AND b.docstatus = 1 AND b.posting_date >= '{}' AND b.posting_date <= '{}' and b.sales_order_type = '{}'
		'''.format(self.customer,frappe.defaults.get_user_default("year_start_date"),frappe.defaults.get_user_default("year_end_date"), self.sales_order_type))[0][0]
		if flt(prev_qty) + flt(qty) > 2 and self.sales_order_type != "Employee Installment":
			frappe.throw(title="Warning",
				msg="You cannot buy more than 2 item from EMI Sales as an Employee")
		elif flt(prev_qty) + flt(qty) > 3 and self.sales_order_type == "Employee Installment":
			frappe.throw(title="Warning",
				msg="You cannot buy more than 3 item from EMI Sales as an Employee")
				
	def create_payment_schedule(self):
		beginning_balance = self.total_receivable_amount - self.no_of_installments_paid * self.monthly_deduction
		if not self.payment_schedule or self.recalculate_amortization == 1:
			if not self.is_on_credit:
				return
			self.set('payment_schedule',[])
			if self.credit_type == 'Due Date Payment':
				row = self.append('payment_schedule',{})
				row.payable_amount = self.net_amount
				row.due_date = self.due_date
			if self.credit_type and self.credit_type in ('Installment Payment') and self.customer_type == "Employee":
				for i in range(int(self.no_of_installation_employee)*12-int(self.no_of_installments_paid)):
					row = self.append('payment_schedule',{})
					row.payable_amount = self.monthly_deduction
					row.beginning_balance = flt(beginning_balance)
					row.interest = flt(beginning_balance) * ((self.interest_percentage * 0.01)/12)
					row.principal = row.payable_amount-row.interest
					row.ending_balance = flt(row.beginning_balance - row.principal)
					if row.ending_balance < 0:
						row.principal += row.ending_balance
						row.ending_balance -= row.ending_balance
						row.payable_amount += row.ending_balance
					beginning_balance = row.ending_balance
					row.due_date = get_last_day(add_months(self.posting_date,i))	
			if self.credit_type and self.credit_type in ('Installment Payment') and self.payment_type == "External Customers Installment" and self.customer_type == "Customer":
				for i in range(int(self.no_of_installation_external)-int(self.no_of_installments_paid)):
					row = self.append('payment_schedule',{})
					row.payable_amount = self.monthly_deduction
					row.beginning_balance = flt(beginning_balance)
					row.interest = flt(beginning_balance) * ((self.interest_percentage * 0.01)/12)
					row.principal = row.payable_amount-row.interest
					row.ending_balance = flt(row.beginning_balance - row.principal)
					beginning_balance = row.ending_balance
					row.due_date = get_last_day(add_months(self.posting_date,i))	

	def check_purchase_limit(self):
		if self.air_time:
			return
		if not self.location_segregation and self.customer_type == 'Customer' and self.customer_group in ['E-Load Distributor','Main Distributor']:
			frappe.throw('Location Segregation is Mandatory for customer {}'.format(self.customer_name))

		if frappe.db.exists({'doctype': 'Customer Group','on_total_amount': 1,'name': self.customer_group}):
			self.purchase_limit_on_total_amount = frappe.db.get_value('Location Segregation Item',{'parent':self.customer_group,'local_segregation':self.location_segregation},['purchase_limit'])
			if not self.purchase_limit_on_total_amount:
				frappe.throw('Purchase Limit is Required for customer group <a href= "#Form/Customer Group/{0}"> <b>{0}</b>'.format(self.customer_group))
			if flt(self.purchase_limit_on_total_amount) > flt(self.grand_total):
				frappe.throw('Amount should not be less than minimium purchase limit <b>{0}</b> for Customer Group <a href= "#Form/Customer Group/{1}"> <b>{1}</b>'.format(self.purchase_limit_on_total_amount,self.customer_group))

		if frappe.db.exists({'doctype': 'Customer Group','on_material_base': 1,'name': self.customer_group}):
			for item in self.items:
				item.purchase_limit = frappe.db.get_value('On Material Base',{'parent':self.customer_group,'mat_sub_group':item.item_subgroup,'location_segregation':self.location_segregation},['purchase_limit'])
				if item.purchase_limit and flt(item.amount) < flt(item.purchase_limit):
					frappe.throw('Amount should not be less than minimium purchase limit <b>{}</b> for item <b>{}</b>'.format(item.purchase_limit,item.item_name))
		
	def update_recovery_details(self):
		if self.is_on_credit and self.customer_type == 'Employee':
			flag     = 0
			self.recovery_start_date = get_first_day(self.posting_date)

			ssl = frappe.db.sql("""
						select
							name,
							docstatus,
							str_to_date(concat(yearmonth,"01"),"%Y%m%d") as salary_month
						from `tabSalary Slip`
						where employee = '{0}'
						and str_to_date(concat(yearmonth,"01"),"%Y%m%d") >= '{1}'
						and docstatus != 2
						order by yearmonth desc limit 1
			""".format(self.customer,str(self.recovery_start_date)),as_dict=True)
			for ss in ssl:
				if not flag:
					flag = 1
					self.recovery_start_date = add_months(str(ss.salary_month),1)
			
			self.db_set("recovery_start_date", self.recovery_start_date)
		self.calculate_monthly_deduction()

	def pmt(self, rate, nper, pv):
		return (pv * rate) / (1 - (1 + rate) ** -nper)


	def update_salary_structure(self, cancel=False):
		if self.is_on_credit and self.customer_type == 'Employee' and self.customer:
			if cancel:
				for ssl in frappe.get_all("Salary Detail", fields=["parent"], filters={"reference_number": self.name, "salary_component": self.salary_component, "parenttype": "Salary Slip", "docstatus": 1}):
					frappe.throw(_('Unable to cancel as salary is already processed. Reference#<u><a href="#Form/Salary Slip/{0}" target="_blank">{0}</a></u>').format(ssl.parent), title="Invalid Operation")
				rem_list = []
				if self.salary_structure:
					doc = frappe.get_doc("Salary Structure", self.salary_structure)
					for d in doc.get("deductions"):
						if d.salary_component == self.salary_component and self.name in (d.reference_number, d.ref_docname):
							rem_list.append(d)
						[doc.remove(d) for d in rem_list]
						doc.save(ignore_permissions=True)
			else:
				if frappe.db.exists("Salary Structure", {"employee": self.customer, "is_active": "Yes"}):
					doc = frappe.get_doc("Salary Structure", {"employee": self.customer, "is_active": "Yes"})
					if flt(doc.net_pay) < flt(self.monthly_deduction):
						frappe.throw('Employee {} take home salary is not sufficient for this transaction'.format(self.customer_name))
					row = doc.append("deductions",{})
					row.salary_component        = self.salary_component
					row.from_date               = self.recovery_start_date
					row.to_date                 = self.recovery_end_date
					row.amount                  = flt(self.monthly_deduction)
					row.default_amount          = flt(self.monthly_deduction)
					row.reference_number        = self.name
					row.reference_name          = self.name
					row.reference_type          = 'EMI Sales'
					row.total_deductible_amount = flt(self.grand_total)
					row.total_deducted_amount   = 0
					row.total_outstanding_amount= flt(self.grand_total)
					row.total_days_in_month     = 0
					row.working_days            = 0
					row.leave_without_pay       = 0
					row.payment_days            = 0
					doc.save(ignore_permissions=True)
					self.db_set("salary_structure", doc.name)
				else:
					frappe.throw(_("No active salary structure found for employee {0} {1}").format(self.customer, self.customer_name), title="No Data Found")


	def calculate_monthly_deduction(self):
		if self.payment_type in ('External Customers Installment','Staff Installment', 'Employee Installment', "Cost Sharing Installment") and self.credit_type == 'Installment Payment':
			if not self.is_on_credit :
				frappe.throw(title='Error',msg='You Need to tick <b>Is On Credit</b> for Payment type <b>{}</b>'.format(self.payment_type))
			remaining_months = month_diff(frappe.defaults.get_user_default("year_end_date"),self.recovery_start_date)

			if flt(remaining_months) < flt(self.no_of_installation) and (self.payment_type != "External Customers Installment" or self.payment_type != "Employee Installment" or self.payment_type != "Cost Sharing Installment"):
				self.no_of_installation = remaining_months+1
			#if required in future --------------------------------------------------------------
			# if self.customer_type == 'Employee':
			# 	employment_type = frappe.db.get_value("Employee",self.customer,"employment_type")
			# 	end_date = 0
			# 	if employment_type == "Contract":
			# 		end_date = frappe.db.get_value("Employee",self.customer,"contract_end_date")
			# 	else:
			# 		end_date = frappe.db.get_value("Employee",self.customer,"date_of_retirement")
			# 	start_date = getdate(self.recovery_start_date)        
			# 	num_months = (end_date.year - start_date.year) * 12 + cint(month_diff(end_date,start_date))
			# 	if flt(self.no_of_installation) > flt(num_months) and flt(remaining_months) < flt(self.no_of_installation):
			# 		self.no_of_installation = num_months
			#----------------end-----------------------------------------------------------------

			# if self.customer_type == "Employee" and self.sales_order_type != "Employee Installment":
			# 	monthly_deduction = flt(self.grand_total) / flt(self.no_of_installation)
			# elif self.customer_type == "Employee" and self.sales_order_type == "Employee Installment":
			# 	monthly_deduction = flt(self.grand_total) / flt(self.no_of_installation_employee)	
			# else:
				# monthly_deduction = flt(self.grand_total) / flt(self.no_of_installation_external)
			# monthly_deduction = self.pmt(flt((self.interest_percentage*0.01)/12), 24, self.total_receivable_amount)
			if self.customer_type == "Employee":
				no_of_installments = self.no_of_installation_employee
			else:
				no_of_installments = self.no_of_installation_external
			if self.interest_percentage > 0:
				monthly_deduction = self.pmt(flt((self.interest_percentage*0.01)/12), flt(no_of_installments)*12, self.total_receivable_amount)
			else:
				monthly_deduction = flt(flt(self.total_receivable_amount)/(flt(no_of_installments)*12),2)
			# self.monthly_deduction = math.ceil(monthly_deduction)
			self.monthly_deduction = flt(monthly_deduction)
			if self.customer_type == "Employee" and self.sales_order_type not in ("Employee Installment", "Cost Sharing Installment"):
				due_date = get_last_day(add_months(self.posting_date,flt(self.no_of_installation)*12))
			elif self.customer_type == "Employee" and self.sales_order_type in ("Employee Installment", "Cost Sharing Installment"):
				due_date = get_last_day(add_months(self.posting_date,flt(self.no_of_installation_employee)*12))	
			else:
				due_date = get_last_day(add_months(self.posting_date,flt(self.no_of_installation_external)*12))
			if getdate(due_date) > getdate(frappe.defaults.get_user_default("year_end_date")) and self.sales_order_type not in ("External Customers", "Employee Installment"):
				self.due_date = frappe.defaults.get_user_default("year_end_date")
			else:
				self.due_date = due_date
			if self.customer_type == 'Employee':
				self.salary_component = 'EMI Sales'
				self.recovery_end_date = self.due_date
		elif self.credit_type == 'Due Date Payment':
			self.monthly_deduction = self.net_amount
		if self.is_existing == 1:
			self.total_receivable_amount = flt(self.total_receivable_amount - self.no_of_installments_paid * self.monthly_deduction, 2)
			self.outstanding_amount = flt(self.total_receivable_amount - self.no_of_installments_paid * self.monthly_deduction, 2)

	@frappe.whitelist()
	def set_status(self, update=False, status=None, update_modified=True):
		if self.is_new():
			if self.get('amended_from'):
				self.status = 'Draft'
			return

		precision = self.precision("outstanding_amount")
		outstanding_amount = flt(self.outstanding_amount, precision)
		due_date = getdate(self.due_date)
		nowdate = getdate()
		discounting_status = None
		if not status:
			if self.docstatus == 2:
				status = "Cancelled"
			elif self.docstatus == 1:
				if outstanding_amount > 0 and due_date < nowdate:
					self.status = "Overdue"
				elif outstanding_amount > 0 and outstanding_amount == self.net_amount:
					self.status = "Not Received"
				elif self.is_return == 1:
					self.status = "Return"
				elif flt(outstanding_amount) > 0 and flt(outstanding_amount) < flt(self.net_amount):
					self.status = "Partially Received"
				elif flt(outstanding_amount)<=0:
					self.status = "Received"
				else:
					self.status = "Submitted"
			else:
				self.status = "Draft"
		if update:
			self.db_set('status', self.status, update_modified = update_modified)

	def post_gl_for_payment(self):
		gl_entries = self.get_gl_entries_for_payment()
		from erpnext.accounts.general_ledger import make_gl_entries
		make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=False, from_repost=False)

	def make_installment_je(self, installment, mode_of_payment, posting_date, cheque_no = None):
		# expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		remaining = multi_installment = 0
		if frappe.db.exists("Employee", {"user_id": frappe.session.user}):
			branch = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "branch")
		else:
			branch = self.branch
		cost_center = frappe.db.get_value("Branch", branch, "cost_center")
		# revenue_bank_account = frappe.db.get_value("Branch", branch, "revenue_bank_account")
		revenue_bank_account = frappe.db.get_single_value("Selling Settings", "default_revenue_bank_account")
		cash_bank_account = None
		interest_income_account = frappe.db.get_value("Company", self.company, "default_interest_income_account")
		income_account = None
		# income_prepaid_account = frappe.db.get_single_value("Selling Settings", "default_income_prepaid_account")
		income_prepaid_account = None
		data_package = 0
		remaining_installment = flt(self.outstanding_amount/self.monthly_deduction,0)
		if self.outstanding_amount > 0 and self.outstanding_amount < 1:
			remaining_installment = 1
		if flt(installment) == remaining_installment and remaining_installment > 1:
			remaining = 1
		elif flt(installment) < flt(remaining_installment) and flt(installment) > 1:
			multi_installment = 1
		# for item in self.items:
		# 	if item.cash_bank_account:
		# 		cash_bank_account = item.cash_bank_account
		# 	if item.data_package:
		# 		data_package = item.data_package
		# 	if item.interest_income_account:
		# 		interest_income_account = item.interest_income_account
		# 	if item.income_account:
		# 		income_account = item.income_account
		if not revenue_bank_account:
			# frappe.throw("Setup Revenue Bank Account in Branch {}".format(branch))
			frappe.throw("Setup Default Revenue Bank Account in Selling Settings")
		if not income_prepaid_account:
			frappe.throw("Setup Default Income from Prepaid Recharge Account in Selling Settings")

		# Journal Entry		
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = 'EMI Sales EMI - ' + str(self.customer) + "(" + self.name + ")" if remaining == 0 else 'EMI Sales Full Payment - ' + str(self.customer) + "(" + self.name + ")"
		je.voucher_type = "Bank Entry"
		je.naming_series = "Bank Receipt Voucher"
		je.emi_sales_installment = 1
		je.company = self.company
		je.branch = branch
		je.remark = 'EMI Payment against EMI Sales: ' + self.name +" \n Mode of Payment: "+mode_of_payment
		je.user_remark = 'EMI Sales EMI - ' + str(self.customer)+" \n Mode of Payment: "+mode_of_payment
		je.posting_date = posting_date
		emi_amount = flt(self.monthly_deduction * installment, 2)
		if (flt(self.outstanding_amount) < self.monthly_deduction) or remaining == 1:
			emi_amount = self.outstanding_amount
		# if remaining == 1:
		# 	data_package = data_package * remaining_installment
		je.append("accounts", {
				"account": revenue_bank_account,
				"debit_in_account_currency": flt(emi_amount,2),
				"debit": flt(emi_amount,2),
				"reference_type": "EMI Sales",
				"reference_name": self.name,
				"cost_center": cost_center,
				"business_activity": "OTB",
		})

		je.append("accounts", {
				"account": cash_bank_account,
				"reference_type": "EMI Sales",
				"reference_name": self.name,
				"cost_center": cost_center,
				"credit_in_account_currency": flt(emi_amount,2),
				"credit": flt(emi_amount,2),
				"business_activity": "OTB",
				"party_type": "Customer",
				"party": self.customer,
			})
		je.append("cheques", {
				"account": revenue_bank_account,
				"cheque_no": cheque_no,
				"pay_to_recd_from": self.customer,
				"posting_date": today(),
				"cheque_date": today(),
				"amount": flt(emi_amount,2),
				"debit": flt(emi_amount,2),

			})
		je.insert()
		je.submit()

		je_references = str(je.name)

		# if flt(self.payable_amount) > 0:
		# jeb_branch = frappe.db.get_single_value("HR Accounts Settings", "le_payment_branch")
		jeb = frappe.new_doc("Journal Entry")
		jeb.flags.ignore_permissions = 1
		jeb.title = "Interest Income from EMI Sales (" + self.customer + ")"
		jeb.voucher_type = "Journal Entry"
		jeb.naming_series = "Journal Voucher"
		jeb.remark = 'Prepaid Income from EMI Sales : ' + self.name +"\n Mode of Payment: "+mode_of_payment
		jeb.user_remark = 'Prepaid Income from EMI Sales : ' + self.name+"\n Mode of Payment: "+mode_of_payment
		jeb.posting_date = posting_date
		jeb.branch = branch
		jeb.emi_sales_installment = 0
		jeb.append("accounts", {
				"account": interest_income_account,
				"reference_type": "EMI Sales",
				"reference_name": self.name,
				"cost_center": cost_center,
				"debit_in_account_currency": self.total_interest_amount,
				"debit": self.total_interest_amount,
				"business_activity": "MBL",
				"party_type": "Customer",
				"party": self.customer
			})

		jeb.append("accounts", {
				"account": income_interest_account if remaining == 0 else income_account,
				"cost_center": cost_center,
				"reference_type": "EMI Sales",
				"reference_name": self.name,
				"credit_in_account_currency": self.total_interest_amount,
				"credit": self.total_interest_amount,
				"business_activity": "MBL",
			})
		jeb.insert()
		jeb.submit()
		je_references = je_references + ", "+ str(jeb.name)

		if multi_installment == 1:
			jep = frappe.new_doc("Journal Entry")
			jep.flags.ignore_permissions = 1
			jep.title = "Prepaid Income from EMI Sales (" + self.customer + " )"
			jep.voucher_type = "Journal Entry"
			jep.naming_series = "Journal Voucher"
			jep.remark = 'Prepaid Income from EMI Sales : ' + self.name + "  \n Mode of Payment: "+mode_of_payment
			jep.user_remark = 'Prepaid Income from EMI Sales : ' + self.name
			jep.posting_date = posting_date
			jep.branch = branch
			jep.emi_sales_installment = 0
			jep.append("accounts", {
					"account": interest_income_account,
					"reference_type": "EMI Sales",
					"reference_name": self.name,
					"cost_center": cost_center,
					"debit_in_account_currency": data_package * (installment - 1),
					"debit": data_package * (installment - 1),
					"business_activity": "MBL",
					"party_type": "Customer",
					"party": self.customer
				})

			jep.append("accounts", {
					"account": income_account,
					"cost_center": cost_center,
					"reference_type": "EMI Sales",
					"reference_name": self.name,
					"credit_in_account_currency": data_package * (installment - 1),
					"credit": data_package * (installment - 1),
					"business_activity": "MBL",
				})
			jep.insert()
			jep.submit()
			je_references = je_references + ", "+ str(jep.name)
		self.set_status(update=True)

	def make_installment_je_prepaid(self, installment, mode_of_payment, posting_date, cheque_no = None):
		# expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		remaining = multi_installment = 0
		if frappe.db.exists("Employee", {"user_id": frappe.session.user}):
			branch = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "branch")
		else:
			branch = self.branch
		cost_center = frappe.db.get_value("Branch", branch, "cost_center")
		# revenue_bank_account = frappe.db.get_value("Branch", branch, "revenue_bank_account")
		revenue_bank_account = frappe.db.get_single_value("Selling Settings", "default_revenue_bank_account")
		cash_bank_account = None
		# interest_income_account = frappe.db.get_single_value("Selling Settings", "default_interest_income_account")
		interest_income_account = frappe.db.get_value("Company", self.company, "default_interest_income_account")
		income_account = None
		# income_prepaid_account = frappe.db.get_single_value("Selling Settings", "default_income_prepaid_account")
		income_prepaid_account = None
		data_package = 0
		remaining_installment = flt(self.outstanding_amount/self.monthly_deduction,0)
		if self.outstanding_amount > 0 and self.outstanding_amount < 1:
			remaining_installment = 1
		if flt(installment) == remaining_installment and remaining_installment > 1:
			remaining = 1
		elif flt(installment) < flt(remaining_installment) and flt(installment) > 1:
			multi_installment = 1
		for item in self.items:
			if item.cash_bank_account:
				cash_bank_account = item.cash_bank_account
			if item.data_package:
				data_package = item.data_package
			if item.interest_income_account:
				interest_income_account = item.interest_income_account
			if item.income_account:
				income_account = item.income_account
		if not revenue_bank_account:
			# frappe.throw("Setup Revenue Bank Account in Branch {}".format(branch))
			frappe.throw("Setup Default Revenue Bank Account in Selling Settings")
		if not income_prepaid_account:
			frappe.throw("Setup Default Income from Prepaid Recharge Account in Selling Settings")

		# if flt(self.payable_amount) > 0:
		# jeb_branch = frappe.db.get_single_value("HR Accounts Settings", "le_payment_branch")
		jeb = frappe.new_doc("Journal Entry")
		jeb.flags.ignore_permissions = 1
		jeb.title = "Prepaid Income from EMI Sales (" + self.customer + ")"
		jeb.voucher_type = "Journal Entry"
		jeb.naming_series = "Journal Voucher"
		jeb.remark = 'Prepaid Income from EMI Sales : ' + self.name +"\n Mode of Payment: "+mode_of_payment
		jeb.user_remark = 'Prepaid Income from EMI Sales : ' + self.name+"\n Mode of Payment: "+mode_of_payment
		jeb.posting_date = posting_date
		jeb.branch = branch
		jeb.emi_sales_installment = 0
		jeb.append("accounts", {
				"account": interest_income_account,
				"reference_type": "EMI Sales",
				"reference_name": self.name,
				"cost_center": cost_center,
				"debit_in_account_currency": data_package,
				"debit": data_package,
				"business_activity": "MBL",
				"party_type": "Customer",
				"party": self.customer
			})

		jeb.append("accounts", {
				"account": income_prepaid_account if remaining == 0 else income_account,
				"cost_center": cost_center,
				"reference_type": "EMI Sales",
				"reference_name": self.name,
				"credit_in_account_currency": data_package,
				"credit": data_package,
				"business_activity": "MBL",
			})
		jeb.insert()
		jeb.submit()
		# je_references = je_references + ", "+ str(jeb.name)

		if multi_installment == 1:
			jep = frappe.new_doc("Journal Entry")
			jep.flags.ignore_permissions = 1
			jep.title = "Prepaid Income from EMI Sales (" + self.customer + " )"
			jep.voucher_type = "Journal Entry"
			jep.naming_series = "Journal Voucher"
			jep.remark = 'Prepaid Income from EMI Sales : ' + self.name + "  \n Mode of Payment: "+mode_of_payment
			jep.user_remark = 'Prepaid Income from EMI Sales : ' + self.name
			jep.posting_date = posting_date
			jep.branch = branch
			jep.emi_sales_installment = 0
			jep.append("accounts", {
					"account": interest_income_account,
					"reference_type": "EMI Sales",
					"reference_name": self.name,
					"cost_center": cost_center,
					"debit_in_account_currency": data_package * (installment - 1),
					"debit": data_package * (installment - 1),
					"business_activity": "MBL",
					"party_type": "Customer",
					"party": self.customer
				})

			jep.append("accounts", {
					"account": income_account,
					"cost_center": cost_center,
					"reference_type": "EMI Sales",
					"reference_name": self.name,
					"credit_in_account_currency": data_package * (installment - 1),
					"credit": data_package * (installment - 1),
					"business_activity": "MBL",
				})
			jep.insert()
			jep.submit()
			# je_references = je_references + ", "+ str(jep.name)
		self.set_status(update=True)
	def account_type(self,account):
		party = party_type = ''
		account_type = frappe.db.get_value('Account',account,'account_type')
		if account_type in ['Payable','Receivable']:
			party = self.customer
			party_type = self.customer_type
		else:
			party = party_type = ''
		return party, party_type

	# def cancel_budget(self):
	# 	if self.required_commission:
	# 		frappe.db.sql("delete from `tabConsumed Budget` where reference_type = %s and reference_no = %s",(str(self.doctype), str(self.name)))
	
	def consume_budget(self):
		# check budget only for commission account
		if self.required_commission:
			for item in self.items:
				check_budget_available(item.cost_center,item.commission_account,self.posting_date,item.commission_amount)
				cc_doc = frappe.get_doc("Cost Center", item.cost_center)
				if cc_doc.use_budget_from_parent:
					cost_center = cc_doc.parent_cost_center
				else:
					cost_center = item.cost_center
				consume = frappe.get_doc({
							"doctype": "Consumed Budget",
							"account": item.commission_account,
							"cost_center": cost_center,
							"reference_type": self.doctype,
							"reference_no": self.name,
							"reference_date": self.posting_date,
							"amount": item.commission_amount,
							"reference_id": item.name
						})
				consume.flags.ignore_permissions=1
				consume.submit()

	@frappe.whitelist()
	def calculate_down_payment(self, rate):
		down_payment = 0
		if self.sales_order_type == "Cost Sharing Installment" and rate > 0 and self.is_existing == 0:
			if self.customer_type != "Employee":
				frappe.throw("Cost sharing installment is only applicable for Employees.")
			quota = frappe.db.get_value("Employee Grade", frappe.db.get_value("Employee", self.customer, "grade"), "cost_sharing_quotaamount")
			if rate > quota:
				down_payment = flt(rate-quota,2)
		return down_payment

	def get_gl_entries_for_payment(self):
		# commission_account	= frappe.db.get_single_value('Selling Settings','default_commission_account')
		# tds_account			= frappe.db.get_single_value('Selling Settings','default_tds_account')
		discount_account 	= frappe.db.get_value('Company', self.company, 'default_discount_account')
		for a in self.items:
			income_account = a.income_account
		# tds_deducted_by_customer_account = frappe.db.get_single_value('Accounts Settings','tds_deducted')
		bank_account = frappe.db.get_value("Company", self.company, "default_bank_account")
		gl_entries = []
		club_amt_ba_wise = frappe._dict()
		count = 1
		party_type = self.customer_type
		party = self.customer
		no_of_installation = 0
		if self.down_payment == 1 and self.down_payment_amount > 0 and self.is_existing == 0:
			gl_entries.append(
				self.get_gl_dict({
					"account": bank_account,
					"against": self.customer,
					"debit": flt(self.down_payment_amount,2),
					"party_type":party_type,
					"party":party,
					"debit_in_account_currency": flt(self.down_payment_amount,2),
					"cost_center": self.cost_center,
					"company":self.company,
					"currency":self.currency
				}))
			gl_entries.append(
				self.get_gl_dict({
					"account": income_account,
					"against": self.customer,
					"credit": flt(self.down_payment_amount,2),
					"credit_in_account_currency": flt(self.down_payment_amount,2),
					"cost_center": self.cost_center,
					"company":self.company,
					"currency":self.currency
				}))

		for item in self.items:
			# frappe.msgprint("Here "+str(item.interest_income_account))
			row = frappe._dict({'commission_amount':0,'tds_amount':0,
								'tds_deducted_by_customer':0,'discount_amount':0,
								'business_activity':item.business_activity,
								'net_amount':0})
			if flt(item.rate) > 0:
				if self.required_commission:
					row['commission_amount'] = item.commission_amount
					row['tds_amount'] = item.tds_amount
				elif self.is_discounted:
					row['discount_amount'] = item.discount_amount
				elif flt(item.tds_deducted_by_customer) > 0:
					row['tds_deducted_by_customer'] = item.tds_deducted_by_customer
				row.net_amount = item.total_amount_received

				account_currency = get_account_currency(item.income_account)
				party, party_type = self.account_type(item.income_account)
				prepaid_party, prepaid_party_type = self.account_type(item.interest_income_account)
				if self.payment_type not in ("External Customers", "Employee Installment", "Cost Sharing Installment"):
					gl_entries.append(
						self.get_gl_dict({
							"account": item.income_account,
							"against": self.customer,
							"credit": flt(item.amount-self.no_of_installments_paid * self.monthly_deduction,2),
							"party_type":party_type,
							"party":party,
							"credit_in_account_currency": (flt(item.amount-self.no_of_installments_paid * self.monthly_deduction, item.precision("amount"))
								if account_currency==self.company_currency
								else flt(item.amount-self.no_of_installments_paid * self.monthly_deduction, item.precision("amount"))),
							"cost_center": item.cost_center,
							"business_activity": item.business_activity,
							"company":self.company,
							"currency":self.currency
						}, account_currency, item=item))
				else:
					amount = flt(flt(item.rate)*flt(item.qty)-flt(self.down_payment_amount)-self.no_of_installments_paid * self.monthly_deduction,item.precision("amount"))
					asset_received_account = frappe.db.get_value("Company", self.company, "asset_received_account")
					gl_entries.append(
						self.get_gl_dict({
							"account": item.income_account,
							"against": self.customer,
							"credit": amount,
							"party_type":party_type,
							"party":party,
							"credit_in_account_currency": amount,
							"cost_center": item.cost_center,
							"business_activity": item.business_activity,
							"company":self.company,
							"currency":self.currency
						}, account_currency, item=item))
					if self.sales_order_type == "Cost Sharing Installment":
						gl_entries.append(
							self.get_gl_dict({
								"account": asset_received_account,
								"against": self.customer,
								"debit": flt(item.total_amount_received - self.no_of_installments_paid * self.monthly_deduction,2),
								"party_type":party_type,
								"party":party,
								"debit_in_account_currency": flt(item.total_amount_received - self.no_of_installments_paid * self.monthly_deduction,2),
								"cost_center": item.cost_center,
								"business_activity": item.business_activity,
								"company":self.company,
								"currency":self.currency
							}, account_currency, item=item))
					if not item.interest_income_account:
						item.interest_income_account = frappe.db.get_value("Company", self.company, "default_interest_income_account")
						# item.interest_income_account = frappe.db.get_single_value("Selling Settings", "default_interest_income_account")
					if self.sales_order_type == "External Customers":
						no_of_installation = self.no_of_installation_external * 12
					else:
						no_of_installation = self.no_of_installation_employee * 12
					if item.total_data_package == 0 and item.data_package != 0 and no_of_installation > 0:
						item.total_data_package = flt(item.data_package) * flt(no_of_installation)
					# if frappe.session.user == "Administrator":
					# 	frappe.throw(str(item.total_data_package))
					if self.total_interest_amount > 0:
						gl_entries.append(
							self.get_gl_dict({
								"account": item.interest_income_account,
								"against": self.customer,
								"credit": flt(flt(self.total_interest_amount),item.precision("amount")),
								"party_type":prepaid_party_type,
								"party":prepaid_party,
								"credit_in_account_currency": flt(flt(self.total_interest_amount), item.precision("amount")),
								"cost_center": item.cost_center,
								"business_activity": item.business_activity,
								"company":self.company,
								"currency":self.currency
							}, account_currency, item=item))
				club_amt_ba_wise.setdefault(item.business_activity,[]).append(row)
			count += 1

		if self.is_on_credit or cint(self.is_opening_bal) == 1:
			cash_bank_account =  frappe.db.get_value('Company',self.company,'default_receivable_account')
		else:
			cash_bank_account =  frappe.db.get_value('Company',self.company,'default_cash_account')


		if len(club_amt_ba_wise.keys()) > 1:
			for key, item in club_amt_ba_wise.items():
				row = frappe._dict({'commission_amount':0,'tds_amount':0,
								'tds_deducted_by_customer':0,'discount_amount':0,
								'business_activity':key,'net_amount':0,
								'cost_center':self.cost_center})
				for v in item:
					row.commission_amount 			+= flt(v.commission_amount)
					row.tds_amount 					+= flt(v.tds_amount)
					row.discount_amount 			+= flt(v.discount_amount)
					row.tds_deducted_by_customer 	+= flt(v.tds_deducted_by_customer)
					row.net_amount					+= flt(v.net_amount)
				account_currency = get_account_currency(cash_bank_account)
				party, party_type = self.account_type(cash_bank_account)
				if flt(row.net_amount) > 0:
					gl_entries.append(
						self.get_gl_dict({
							"account": cash_bank_account,
							"party_type":party_type,
							"party":party,
							"debit": row.net_amount,
							"debit_in_account_currency": (flt(row.net_amount, self.precision("net_amount"))
								if account_currency==self.company_currency
								else flt(row.net_amount, self.precision("net_amount"))),
							"cost_center": row.cost_center,
							"business_activity": row.business_activity,
							"company":self.company,
							"currency":self.currency,
							"against_voucher_type":self.doctype,
							"against_voucher":self.name
						}, account_currency))
				# if row.commission_amount > 0:
				# 	account_currency = get_account_currency(commission_account)
				# 	party, party_type = self.account_type(commission_account)
				# 	gl_entries.append(
				# 		self.get_gl_dict({
				# 			"account": commission_account,
				# 			"against": self.customer,
				# 			"party_type":party_type,
				# 			"party":party,
				# 			"debit": row.commission_amount,
				# 			"debit_in_account_currency": flt(row.commission_amount, self.precision("commission_amount"))
				# 				if account_currency == self.company_currency
				# 				else flt(row.commission_amount, self.precision("commission_amount")),
				# 			"company":self.company,
				# 			"currency":self.currency,
				# 			"cost_center": row.cost_center,
				# 			"business_activity": row.business_activity,
				# 		}, account_currency))
				# if row.tds_amount > 0:
				# 	account_currency = get_account_currency(tds_account)
				# 	party, party_type = self.account_type(tds_account)
				# 	gl_entries.append(
				# 		self.get_gl_dict({
				# 			"account": tds_account,
				# 			"party_type":party_type,
				# 			"party":party,
				# 			"against": self.customer ,
				# 			"credit": row.tds_amount,
				# 			"credit_in_account_currency": flt(row.tds_amount, self.precision("tds_amount"))
				# 				if account_currency == self.company_currency
				# 				else flt(row.tds_amount, self.precision("tds_amount")),
				# 			"cost_center": row.cost_center,
				# 			"business_activity": row.business_activity,
				# 			"company":self.company,
				# 			"currency":self.currency
				# 		}, account_currency))
				if row.discount_amount > 0:
					account_currency = get_account_currency(discount_account)
					party, party_type = self.account_type(discount_account)
					gl_entries.append(
						self.get_gl_dict({
							"account": discount_account,
							"debit": row.discount_amount,
							"party_type":party_type,
							"party":party,
							"debit_in_account_currency": flt(row.amount, self.precision("discount_amount"))
								if account_currency==self.company_currency
								else flt(row.amount, self.precision("discount_amount")),
							"cost_center": row.cost_center,
							"business_activity": row.business_activity,
							"company":self.company,
							"currency":self.currency,
							"against_voucher_type":self.doctype,
							"against_voucher":self.name
						}, account_currency))
				# if row.tds_deducted_by_customer > 0:
				# 	account_currency = get_account_currency(tds_deducted_by_customer_account)
				# 	party, party_type = self.account_type(tds_deducted_by_customer_account)
				# 	gl_entries.append(
				# 		self.get_gl_dict({
				# 			"account": tds_deducted_by_customer_account,
				# 			"party_type":party_type,
				# 			"party":party,
				# 			"debit": row.tds_deducted_by_customer,
				# 			"debit_in_account_currency": flt(row.tds_deducted_by_customer, self.precision("tds_deducted_by_customer"))
				# 				if account_currency==self.company_currency
				# 				else flt(row.tds_deducted_by_customer, self.precision("tds_deducted_by_customer")),
				# 			"cost_center": row.cost_center,
				# 			"business_activity": row.business_activity,
				# 			"company":self.company,
				# 			"currency":self.currency,
				# 			"against_voucher_type":self.doctype,
				# 			"against_voucher":self.name
				# 		}, account_currency))
		else:
			for key, item in club_amt_ba_wise.items():
				ba = key
				break
			account_currency = get_account_currency(cash_bank_account)
			party, party_type = self.account_type(cash_bank_account)
			if flt(self.net_amount) > 0:
				gl_entries.append(
					self.get_gl_dict({
						"account": cash_bank_account,
						"party_type":party_type,
						"party":party,
						"debit": self.net_amount,
						"debit_in_account_currency": (flt(self.net_amount, self.precision("net_amount"))
							if account_currency==self.company_currency
							else flt(self.net_amount, self.precision("net_amount"))),
						"cost_center": self.cost_center,
						"business_activity": ba,
						"company":self.company,
						"currency":self.currency,
						"against_voucher_type":self.doctype,
						"against_voucher":self.name
					}, account_currency))
			# if self.commission_amount > 0:
			# 	account_currency = get_account_currency(commission_account)
			# 	party, party_type = self.account_type(commission_account)
			# 	gl_entries.append(
			# 		self.get_gl_dict({
			# 			"account": commission_account,
			# 			"against": self.customer,
			# 			"party_type":party_type,
			# 			"party":party,
			# 			"debit": self.commission_amount,
			# 			"debit_in_account_currency": flt(self.commission_amount, self.precision("commission_amount"))
			# 				if account_currency==self.company_currency
			# 				else flt(self.commission_amount, self.precision("commission_amount")),
			# 			"company":self.company,
			# 			"currency":self.currency,
			# 			"cost_center": self.cost_center,
			# 			"business_activity": ba,
			# 		}, account_currency))
			# if self.tds_amount > 0:
			# 	account_currency = get_account_currency(tds_account)
			# 	party, party_type = self.account_type(tds_account)
			# 	gl_entries.append(
			# 		self.get_gl_dict({
			# 			"account": tds_account,
			# 			"party_type":party_type,
			# 			"party":party,
			# 			"against": self.customer ,
			# 			"credit": self.tds_amount,
			# 			"credit_in_account_currency": flt(self.tds_amount, self.precision("tds_amount"))
			# 				if account_currency==self.company_currency
			# 				else flt(self.tds_amount, self.precision("tds_amount")),
			# 			"cost_center": self.cost_center,
			# 			"business_activity": ba,
			# 			"company":self.company,
			# 			"currency":self.currency
			# 		}, account_currency))
			if self.discount_amount > 0:
				account_currency = get_account_currency(discount_account)
				party, party_type = self.account_type(discount_account)
				gl_entries.append(
					self.get_gl_dict({
						"account": discount_account,
						"debit": self.discount_amount,
						"party_type":party_type,
						"party":party,
						"debit_in_account_currency": flt(self.discount_amount, self.precision("discount_amount"))
							if account_currency==self.company_currency
							else flt(self.discount_amount, self.precision("discount_amount")),
						"cost_center": self.cost_center,
						"business_activity": ba,
						"company":self.company,
						"currency":self.currency,
						"against_voucher_type":self.doctype,
						"against_voucher":self.name
					}, account_currency))
			# if self.total_tds_deducted_by_customer > 0:
			# 	account_currency = get_account_currency(tds_deducted_by_customer_account)
			# 	party, party_type = self.account_type(tds_deducted_by_customer_account)
			# 	gl_entries.append(
			# 		self.get_gl_dict({
			# 			"account": tds_deducted_by_customer_account,
			# 			"party_type":party_type,
			# 			"party":party,
			# 			"debit": self.total_tds_deducted_by_customer,
			# 			"debit_in_account_currency": flt(self.total_tds_deducted_by_customer, self.precision("total_tds_deducted_by_customer"))
			# 				if account_currency==self.company_currency
			# 				else flt(self.total_tds_deducted_by_customer, self.precision("total_tds_deducted_by_customer")),
			# 			"cost_center": self.cost_center,
			# 			"business_activity": ba,
			# 			"company":self.company,
			# 			"currency":self.currency,
			# 			"against_voucher_type":self.doctype,
			# 			"against_voucher":self.name
			# 		}, account_currency))
		return gl_entries
			
	def calculate_amount(self):
		self.cost_sharing_percentage = 100
		if self.sales_order_type and self.customer_group:
			self.cost_sharing_percentage = frappe.db.get_value("EMI Sales Type Item", {"parent": self.sales_order_type, "customer_group": self.customer_group}, "cost_sharing_percentage")
		if cint(self.set_price_date_manually) == 1 and not self.pricing_date:
			frappe.throw("You need to set pricing date for maual pricing date")

		# calculate commission, tds, total 
		total = commission_amount = taxable_amount = tds_amount = base_paid_amount = discount_amount = net_amount = total_tds_deducted_by_customer = total_interest_amount = 0
		ba = self.items[0].business_activity
		for item in self.items:
			if self.sales_order_type in ("External Customers", "Employee Installment", "Cost Sharing Installment"):
				no_of_installation = 0
				if self.sales_order_type == "External Customers":
					no_of_installation = self.no_of_installation_external * 12
				else:
					no_of_installation = self.no_of_installation_employee * 12
				if item.total_data_package == 0 and item.data_package != 0 and flt(no_of_installation) > 0:
					item.total_data_package = flt(item.data_package) * flt(no_of_installation)
				
			item.stock_qty = item.qty
			item.amount = item.qty * item.rate
			item.amount += item.total_data_package

			# Restrict to sell on different BA as it gives issue while making payment entry. applies to credit sell only
			if self.is_on_credit and ba != item.business_activity:
				frappe.throw(title="Error",msg="You cannot sell material with different Business Actvity like <b>{}</b> and <b>{}</b> on Credit.We suggest you to make different transaction for different business activity.This applies to Credit sale only".format(ba,item.business_activity))
			if item.item_group != 'Services':
				# check item qty available
				# if flt(item.qty) > flt(item.actual_qty):
				# 	frappe.throw('There is not enough qty of item <b>{}</b> in warehouse <b>{}</b>'.format(item.item_code,item.warehouse))
				# fetch selling price of item
				sp = 0
				# if self.customer_type == "Employee" and self.sales_order_type != "Employee Installment":
				# 	sp = get_selling_rate(self.company,item.item_code,self.pricing_date if cint(self.set_price_date_manually) == 1 else self.posting_date,item.item_group,self.payment_type, no_of_installation=self.no_of_installation)
				# elif self.customer_type == "Employee" and self.sales_order_type == "Employee Installment":
				# 	sp = get_selling_rate(self.company,item.item_code,self.pricing_date if cint(self.set_price_date_manually) == 1 else self.posting_date,item.item_group,self.payment_type, no_of_installation=self.no_of_installation_employee)	
				# else:
				# 	sp = get_selling_rate(self.company,item.item_code,self.pricing_date if cint(self.set_price_date_manually) == 1 else self.posting_date,item.item_group,self.payment_type, no_of_installation=self.no_of_installation_external)
				if sp and not item.is_foc_item:
					conversion_factor = self.check_conversion_factor(item.item_code, item.uom)
					item.rate = flt(sp['selling_price']/flt(conversion_factor),2)
					item.selling_price = sp['name']
			item.commission_percent = 0
			item.tds_percent = 0
			item.taxable_percent = 0
			item.commission_amount = 0
			item.taxable_amount = 0	
			item.tds_amount = 0
			item.total_amount_received = flt(item.amount,2)

			if self.is_discounted :
				if item.discount_percent :
					item.discount_amount = flt(flt(item.discount_percent) * flt(item.amount) / 100,2)
				discount_amount += flt(item.discount_amount)
				item.total_amount_received = flt(flt(item.amount) - flt(item.discount_amount),2)
			else:
				item.discount_amount = 0
				item.discount_percent = 0

			if flt(item.tds_deducted_by_customer) > 0:
				item.total_amount_received = flt(flt(item.total_amount_received) - flt(item.tds_deducted_by_customer),2)
			else:
				item.tds_deducted_by_customer = 0
			if self.down_payment:
				item.total_amount_received -= flt(self.down_payment_amount,2)
			cost_sharing_per = frappe.db.get_value("EMI Sales Type Item", {"parent": self.sales_order_type, "customer_group": self.customer_group}, "cost_sharing_percentage")
			if not cost_sharing_per:
				cost_sharing_per = 100
			item.total_amount_received = item.total_amount_received * cost_sharing_per * 0.01
			# if self.interest_percentage:
			# 	item.interest_amount = item.total_amount_received * self.interest_percentage * 0.01
			# 	item.total_amount_received += item.interest_amount
			# assign cost_center and warehouse
			item.cost_center = self.cost_center
			item.warehouse = self.delivery_warehouse
			total += flt(item.amount)
			commission_amount += flt(item.commission_amount)
			taxable_amount += flt(item.taxable_amount)
			tds_amount += flt(item.tds_amount)
			item.base_amount = flt(flt(item.amount) * flt(self.conversion_rate), self.precision("base_paid_amount"))
			base_paid_amount += flt(item.base_amount)
			net_amount += flt(item.total_amount_received)
			total_tds_deducted_by_customer += flt(item.tds_deducted_by_customer)
		for ps in self.payment_schedule:
			total_interest_amount += flt(ps.interest, 2)
		self.total_interest_amount = total_interest_amount
		self.total_tds_deducted_by_customer = flt(total_tds_deducted_by_customer,2)
		# self.grand_total = flt(total,2)
		self.commission_amount = flt(commission_amount,2)
		self.taxable_amount = flt(taxable_amount,2)
		self.tds_amount = flt(tds_amount,2)
		self.base_paid_amount = flt(base_paid_amount,2)
		self.discount_amount = flt(discount_amount,2)
		self.total_receivable_amount = flt(net_amount,2)
		self.grand_total = flt(flt(self.total_receivable_amount,2)+flt(self.total_interest_amount,2),2)
		self.net_amount = flt(self.grand_total,2)
		self.total_tds_amount = self.tds_amount
		
		if self.docstatus == 1 and not self.is_on_credit and cint(self.is_opening_bal) != 1:
			self.outstanding_amount = 0 
		elif self.docstatus == 0 :
			self.outstanding_amount = self.grand_total
		elif self.docstatus == 2:
			self.outstanding_amount =  self.grand_total

		if self.required_commission:
			if flt(self.commission_amount) <= 0 :
				frappe.throw('Commission Amount is required for this Transaction')

	@frappe.whitelist()
	def check_conversion_factor(self, item_code, uom):
		if item_code:
			if not uom:
				frappe.throw("Please select UOM.")
			conversion_factor = frappe.db.get_value("UOM Conversion Detail", {"parent": item_code, "uom": uom}, "conversion_factor")
			if conversion_factor:
				return conversion_factor

	def post_stock_ledger(self):
		for item in self.items:
			doc = frappe.new_doc("Stock Ledger Entry")
			doc.item_code = item.item_code
			doc.warehouse = self.delivery_warehouse
			doc.posting_date = self.posting_date
			doc.posting_time = self.posting_time
			doc.voucher_type = "EMI Sales"
			doc.voucher_no = self.name
			doc.actual_qty = item.actual_qty
			doc.valuation_rate = item.rate
			doc.save(ignore_permissions=True)
			doc.submit()

	# fetch customer Details
	@frappe.whitelist()
	def get_customer_details(self):
		if not self.customer:
			return 
		if self.customer_type == 'Customer':
			self.customer_name, self.customer_group, self.customer_email = frappe.db.get_value('Customer',self.customer,['customer_name','customer_group','email_id'])
			# fetch purchase limit if applicable for total amount base on customer group
			#change for stcbl
			# if frappe.db.exists({'doctype': 'Customer Group','on_total_amount': 1,'name': self.customer_group}):
			# 	self.purchase_limit_on_total_amount = frappe.db.get_value('Location Segregation Item',{'parent':self.customer_group,'local_segregation':self.location_segregation},['purchase_limit'])

		elif self.customer_type == 'Employee':
			self.customer_name, self.customer_group = frappe.db.get_value('Employee',self.customer,['employee_name','customer_group'])
		interest = 0
		count = frappe.db.get_value("select count(name) count from `tabEMI Sales` where customer = '{}' and docstatus = 1 and status != 'Paid'".format(self.customer), as_dict=1)
		if not count:
			count = 0
		else:
			count = count[0].count
		if self.sales_order_type == "Cost Sharing Installment":
			if count > 0:
				interest = 7
		else:
			interest = 12

		return interest

	# assign warehouse if there is only one
	@frappe.whitelist()
	def fetch_warehouse(self):
		data = frappe.db.sql('''select parent from `tabWarehouse Branch` where branch = '{0}'
		'''.format(self.branch), as_dict=1)
		if len(data) == 1:
			self.delivery_warehouse = data[0].parent
	def fetch_sales_order_type(self):
		data = frappe.db.sql('''
				SELECT p.name FROM `tabSales Order Type Item` i, `tabSales Order Type` p
				where i.customer_group = '{0}' and p.name = p.parent and p.disabled = 0
			'''.format(self.customer_group), as_dict=True)
		if len(data) == 1:
			self.sales_order_type = data[0].parent
			self.required_commission = frappe.db.get_value('Sales Order Type',self.sales_order_type,'required_commission')
	@frappe.whitelist()
	def get_payment_type(self):
		cond = ''
		# if self.customer_type == 'Employee':
		cond = " and allowed_credit = {is_on_credit}".format(is_on_credit= self.is_on_credit)
		data = frappe.db.sql("""select i.parent from `tabPayment Type Item` i WHERE i.customer_group = '{customer_group}'
                    AND i.sales_order_type = '{sales_order_type}'
					AND EXISTS (select 1 from `tabPayment Type` where name = i.parent {cond})
					""".format(customer_group = self.customer_group, sales_order_type = self.sales_order_type, cond = cond ),as_dict=1)
		if len(data) == 1:
			self.payment_type = data[0].parent
			return data[0].parent
		else:
			self.payment_type = None
			return None
			
def get_permission_query_conditions(user):
	# restrick user from accessing this doctype
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator":
		return
	if "Sales Master" in user_roles:
		return
	if "External Auditor" in user_roles:
		return

	return """(
		`tabEMI Sales`.owner = '{user}'
		or
		exists(select 1
				from `tabEmployee`
				where `tabEmployee`.branch = `tabEMI Sales`.branch
				and `tabEmployee`.user_id = '{user}'
				and exists(select 1 from `tabHas Role` where role = 'Sales Manager' and parent = '{user}'))
		or
        exists(select 1
            from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
            where e.user_id = '{user}'
            and ab.employee = e.name
            and bi.parent = ab.name
            and bi.branch = `tabEMI Sales`.branch)
		or
		exists(select 1
			from `tabEmployee`
			where `tabEmployee`.user_id = '{user}'
			and `tabEmployee`.branch = `tabEMI Sales`.branch
			and `tabEMI Sales`.customer_type = 'Customer'
			and `tabEMI Sales`.is_on_credit = 1
			and `tabEMI Sales`.docstatus = 1
			)
		or 
		exists(select 1
			from `tabEmployee`
			where `tabEmployee`.user_id = '{user}'
			and `tabEmployee`.branch = `tabEMI Sales`.branch
			and `tabEMI Sales`.customer_type = 'Employee'
			and `tabEMI Sales`.is_on_credit = 1
			and `tabEMI Sales`.docstatus = 1
			)
		)""".format(user=user)

@frappe.whitelist()
def set_actual_qty(item_code,warehouse):
	actual_qty = frappe.db.sql("""select actual_qty from `tabBin`
		where item_code = %s and warehouse = %s""", (item_code, warehouse))
	actual_qty = actual_qty and flt(actual_qty[0][0]) or 0
	return actual_qty

@frappe.whitelist()
def get_default_income_account(item_code, company):
	# acc = frappe.db.get_value("Item",{'name':item_code},["credit_or_debit_acc"])
	# if not frappe.db.get_value("Company", company, "default_interest_income_account"):
	# if not frappe.db.get_value("Company", company, "default_prepaid_expense_account"):
	# 	frappe.throw("Please set Default Prepaid Expense Account in Company Settings.".format(company))
	row = {}
	# if acc:
	# 	row['income_account'] = acc
	# 	return row
	income_acc, exp_acc = frappe.db.get_value("Item Default",{"parent":item_code},["income_account","expense_account"])
	row['income_account'] = income_acc
	row['expense_account'] = exp_acc
	# row['interest_income_account'] = frappe.db.get_single_value("Selling Settings", "default_interest_income_account")
	row['interest_income_account'] = frappe.db.get_value("Company", company, "default_interest_income_account")
	return row
@frappe.whitelist()
def apply_item_filter(doctype, txt, searchfield, start, page_len, filters):
	cond = ''
	txt = txt.replace("'", "''")
	if frappe.db.exists({'doctype': 'Customer Group','apply_material_restriction': 1,'name': filters['customer_group']}):
		cond = " AND EXISTS (SELECT 1 FROM `tabRestricted Item Sub Group` where parent = '{}' and sub_group = i.item_sub_group)".format(filters['customer_group'])
	return frappe.db.sql("""select i.name, i.item_name, i.item_group, i.item_sub_group from `tabItem` i
			where i.item_group IN ('Vehicle', 'Sales Product')
			AND i.disabled = 0 AND i.is_sales_item = 1 
			AND (`{key}` LIKE %(txt)s OR i.item_name LIKE %(txt)s OR i.item_group LIKE %(txt)s OR i.item_sub_group LIKE %(txt)s )
			{cond}
			order by name limit %(start)s, %(page_len)s"""
			.format(key=searchfield, cond = cond), {
				'txt': '%' + txt + '%',
				'start': start, 'page_len': page_len
			})

@frappe.whitelist()
def get_payment_type(doctype, txt, searchfield, start, page_len, filters):
	cond = ''
	txt = txt.replace("'", "''")
	# frappe.throw("here")
	if filters.get('customer_group') == 'Internal':
		cond += " and allowed_credit ='{}'".format(filters.get('is_on_credit'))
	# frappe.throw("here "+str(frappe.db.sql("""select i.parent from `tabPayment Type Item` i WHERE i.customer_group = '{customer_group}'
    #         AND i.sales_order_type == "{sales_order_type}"
	# 		AND (`{key}` LIKE %(txt)s OR i.customer_group LIKE %(txt)s OR i.sales_order_type LIKE %(txt)s)
	# 		AND EXISTS (select 1 from `tabPayment Type` where name = i.parent {cond})
	# 		order by parent limit %(start)s, %(page_len)s"""
	# 		.format(key=searchfield, customer_group = filters['customer_group'], sales_order_type = filters['sales_order_type'], cond = cond), {
	# 			'txt': '%' + txt + '%',
	# 			'start': start, 'page_len': page_len
	# 		})))
	if filters.get('customer_group') and filters.get('sales_order_type'):
		return frappe.db.sql("""select i.parent from `tabPayment Type Item` i WHERE i.customer_group = '{customer_group}'
				AND i.sales_order_type = '{sales_order_type}'
				AND (`{key}` LIKE %(txt)s OR i.customer_group LIKE %(txt)s OR i.sales_order_type LIKE %(txt)s)
				AND EXISTS (select 1 from `tabPayment Type` where name = i.parent {cond})
				order by parent limit %(start)s, %(page_len)s"""
				.format(key=searchfield, customer_group = filters.get('customer_group'), sales_order_type = filters.get('sales_order_type'), cond = cond), {
					'txt': '%' + txt + '%',
					'start': start, 'page_len': page_len
				})
	else:
		return []
		
@frappe.whitelist()
def get_sales_order(doctype, txt, searchfield, start, page_len, filters):
	cond = ''
	txt = txt.replace("'", "''")
	interest = 0
	count = frappe.db.get_value("select count(name) count from `tabEMI Sales` where customer = '{}' and docstatus = 1 and status != 'Paid'".format(self.customer), as_dict=1)
	if not count:
		count = 0
	else:
		count = count[0].count
	if int(count) > 0:
		interest = 7
	if txt:
		cond += ' or `tabEMI Sales Type Item`.customer_group like "{}"'.format(txt)
	if filters['customer_type'] != 'Customer':
		data = frappe.db.sql('''
					SELECT parent FROM `tabEMI Sales Type Item`
					where customer_group = '{0}' {1}
				'''.format(filters['customer_group'],cond))
	else:
		# if filters['customer']:
		# 	data = frappe.db.sql('''
		# 		SELECT soti.parent FROM `tabEMI Sales Type Item` soti, `tabEMI Sales Type` sot, `tabCustomer` c
		# 		where soti.customer_group = '{0}'
		# 		and soti.customer_group = c.customer_group
		# 		and soti.parent = sot.name
		# 		and c.name = "{1}"
		# 		and case when c.link_to_sales_order_type = 1 then exists (select 1 from `tabCustomer Order Type` cot where cot.parent = c.name and soti.parent = cot.sales_order_type)
		# 		else 1 = 1 end
		# 		and case when sot.restrict = 1 then exists (select 1 from `tabCustomer Order Type` cot where cot.parent = c.name and soti.parent = cot.sales_order_type)
		# 		else 1 = 1 end
		# 	'''.format(filters['customer_group'], filters['customer']))
		# else:
		data = frappe.db.sql('''
					SELECT `tabEMI Sales Type Item`.parent FROM `tabEMI Sales Type Item`
					where `tabEMI Sales Type Item`.customer_group = '{0}'
					{1}
				'''.format(filters['customer_group'],cond))
	return data

# get customer base on branch
@frappe.whitelist()
def apply_customer_filter(doctype, txt, searchfield, start, page_len, filters):
	cond = ''
	txt = txt.replace("'", "''")
	if not filters.get("branch") and filters.get("sales_order_type") != "External Customers":
		frappe.throw("Please Select Branch first")
	# if filters.get("sales_order_type") != "External Customers":
	# 	if filters['branch']:
	# 		if filters['customer_type'] == "Employee":
	# 			cond = ' AND branch = "{0}" '.format(filters['branch'])
	# 		# else:
	# 		# 	cond = ' AND (branch = "{0}" OR common_customer = 1)'.format(filters['branch'])
	# if filters.get("sales_order_type") == "External Customers":
	# 	cond = ' AND customer_group in ('')'
	if filters['customer_type'] == 'Customer':
		if filters.get('sales_order_type'):
			return frappe.db.sql('''
				SELECT name, customer_name, customer_group, mobile_no
				FROM `tabCustomer`
				WHERE disabled = 0 AND docstatus != 2
				AND CASE WHEN link_to_sales_order_type = 1 THEN exists (SELECT 1 FROM `tabCustomer Order Type` where `tabCustomer Order Type`.sales_order_type = '{sales_order_type}' and `tabCustomer Order Type`.parent = `tabCustomer`.name)
				ELSE 1 = 1 END
				AND	(`{key}` LIKE %(txt)s OR customer_name LIKE %(txt)s 
					OR mobile_no LIKE %(txt)s)
				{cond}
				ORDER BY parent LIMIT %(start)s, %(page_len)s
			'''.format(key=searchfield, sales_order_type = filters['sales_order_type'], cond = cond),{
					'txt': '%' + txt + '%',
					'start': start, 'page_len': page_len
				})
		else:
			return frappe.db.sql('''
				SELECT name, customer_name, customer_group, mobile_no
				FROM `tabCustomer`
				WHERE disabled = 0 AND docstatus != 2
				AND	(`{key}` LIKE %(txt)s OR customer_name LIKE %(txt)s 
					OR mobile_no LIKE %(txt)s)
				{cond}
				ORDER BY name LIMIT %(start)s, %(page_len)s
			'''.format(key=searchfield, cond = cond),{
					'txt': '%' + txt + '%',
					'start': start, 'page_len': page_len
				})
	elif filters['customer_type'] == 'Employee':
		return frappe.db.sql('''
			SELECT name, employee_name, branch
			FROM `tabEmployee`
			WHERE status = 'Active'
			AND(`{key}` LIKE %(txt)s OR employee_name LIKE %(txt)s )
			{cond}
			ORDER BY name LIMIT %(start)s, %(page_len)s
		'''.format(key=searchfield, cond = cond),{
				'txt': '%' + txt + '%',
				'start': start, 'page_len': page_len
			})
	# elif filters['customer_type'] == 'Employee':
	# 	return frappe.db.sql('''
	# 		SELECT name, employee_name, customer_group, branch
	# 		FROM `tabEmployee`
	# 		WHERE status = 'Active'
	# 		AND(`{key}` LIKE %(txt)s OR employee_name LIKE %(txt)s 
	# 			OR name LIKE %(txt)s OR customer_group LIKE %(txt)s)
	# 		ORDER BY parent LIMIT %(start)s, %(page_len)s
	# 	'''.format(key=searchfield),{
	# 			'txt': '%' + txt + '%',
	# 			'start': start, 'page_len': page_len
	# 		})
	
# get warehouse which have branch present in it
@frappe.whitelist()
def get_warehouse(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql('''
		select parent, branch from `tabWarehouse Branch` where branch = '{0}'
		AND(`{key}` LIKE %(txt)s OR parent LIKE %(txt)s)
		ORDER BY parent LIMIT %(start)s, %(page_len)s
	'''.format(filters['branch'],key=searchfield),{
				'txt': '%' + txt + '%',
				'start': start, 'page_len': page_len
			})

# fetch purchase limit for item sub group if applicable itx
# its applicable for e-load distributor
@frappe.whitelist()
def get_purchase_limit(customer_group, item_code, customer):
	if customer == 'Employee':
		return None
	location_segregation = frappe.db.get_value('Customer',customer,['location_segregation'])
	if frappe.db.exists({'doctype':'Customer Group', 'name':customer_group,	'on_material_base':1}):
		item_sub_group = frappe.get_value('Item',item_code,['item_sub_group'])
		return frappe.db.get_value('On Material Base',{'parent':customer_group,'mat_sub_group':item_sub_group,'location_segregation':location_segregation},['purchase_limit'])
	else:
		return None

@frappe.whitelist()
def extend_due_date(next_due_date, doc_type, name):
	doc = frappe.get_doc(doc_type,name)
	if getdate(doc.due_date) > getdate(next_due_date):
		frappe.throw('Next due date cannot be lesser than current due date')
	if doc.credit_type == 'Due Date Payment' and doc.is_on_credit:
		doc.due_date = next_due_date
		doc.payment_schedule[0].due_date = next_due_date
		doc.save(ignore_permissions=True)
	return 1
		# frappe.msgprint(str(next_due_date))
