# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import urllib.parse
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate, getdate, formatdate
from frappe.model.mapper import get_mapped_doc
#from nowdate import nowdate 
from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states

class TargetSetUp(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.pms.doctype.performance_target_evaluation.performance_target_evaluation import PerformanceTargetEvaluation
		from frappe.types import DF

		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Data | None
		approver_name: DF.Data | None
		branch: DF.Link | None
		company: DF.Link | None
		date: DF.Date | None
		designation: DF.Link | None
		division: DF.Link | None
		eas_calendar: DF.Link
		eas_group: DF.Link
		employee: DF.Link
		employee_name: DF.ReadOnly | None
		end_date: DF.Date | None
		grade: DF.Link | None
		reason: DF.Data | None
		section: DF.Link | None
		start_date: DF.Date | None
		target_item: DF.Table[PerformanceTargetEvaluation]
		unit: DF.Link | None
	# end: auto-generated types
	def validate(self):
		self.check_target()
		self.check_duplicate_entry() 
		validate_workflow_states(self) 
		self.validate_calendar()

	def before_submit(self):
		self.validate_calendar()

			
	def on_submit(self):
		return
		#self.validate_calendar()

	def on_update_after_submit(self):
		self.check_target()
		review = frappe.db.get_value('Review', {'target':self.name,'docstatus':('!=',2)}, ['name'])
		if not review:
			return
		rev_doc = frappe.get_doc('Review',review)
		for r, t in zip(rev_doc.review_target_item,self.target_item):
			r.from_date = t.from_date
			r.to_date = t.to_date
		
		rev_doc.save(ignore_permissions=True)

		evaluation = frappe.db.get_value('Performance Evaluation',{'review':review,'docstatus':('<',2)},['name'])
		if not evaluation :
			return
		eval_doc = frappe.get_doc('Performance Evaluation',evaluation)
			
		for e, t in zip(eval_doc.evaluate_target_item,self.target_item):
			r.from_date = t.from_date
			r.to_date = t.to_date

		eval_doc.save(ignore_permissions = True)


	# kinzang.n Added. To validate the date range from eas calendar target start date and end date. Employee can create target set up with eas calendar date range.
	def validate_calendar(self):
		"""
		Validate that Target Set Up can only be created within the allowed date range
		for the employee's EAS Group in the selected EAS Calendar.
		"""
		
		# Check if this is an amended/cancelled Target
		if self.amended_from:
			doc = frappe.get_doc("Target Set Up", self.amended_from)
			if self.eas_calendar != doc.eas_calendar:
				frappe.throw(_("EAS Calendar does not match with the cancelled Target"))
			return
		#Only validate for Draft / Rejected
		# if self.workflow_state not in ["Draft", "Rejected"]:
		# 	return

		if self.docstatus == 2:
			return
		
		current_date = getdate()
		
		#Get the selected EAS Calendar
		
		eas_calendar = frappe.get_doc("EAS Calendar", self.eas_calendar)
		
		#Loop through items to find matching EAS Group
		active_found = False
		allowed_ranges = []
		
		for item in eas_calendar.get("items", []):
			if item.eas_group != self.eas_group:
				continue
			
			start_date = getdate(item.target_start_date)
			end_date = getdate(item.target_end_date)
			
			allowed_ranges.append(f"{formatdate(start_date)} to {formatdate(end_date)}")
			
			if start_date <= current_date <= end_date:
				active_found = True
				break
			
		#Throw error if current date is not within allowed range
		if not active_found:
			frappe.throw(_(
				"Target Set Up for <b>{group}</b> can only be created/approve within the allowed date range(s) in EAS Calendar <b>{calendar}</b>: <b>{ranges}</b>"
			).format(
				group=self.eas_group,
				calendar=self.eas_calendar,
				ranges=", ".join(allowed_ranges)
			))
	
 # till  here added bt kinzang.n




		
	# def validate_calendar(self):
		
	# 	if frappe.db.exists("Target Set Up", {"employee": self.employee, "docstatus":2, "eas_calendar": self.eas_calendar}):
	# 		doc = frappe.get_doc('Target Set Up', self.amended_from)
			
	# 		if self.eas_calendar == doc.eas_calendar:
	# 			#
	# 			return
	# 		else:
	# 			frappe.throw(_("EAS Calendar doesnot match with the cancelled Target"))

		
	# 	if self.eas_group in ['Group I', 'Group II'] and self.workflow_state in ['Draft', 'Rejected']:
	# 		current_date = getdate()
	# 		eas_calendar = frappe.get_doc("EAS Calendar", self.eas_calendar)
	# 		active_found = False

	# 		for child in eas_calendar.get("items", []):
	# 			if child.eas_group != self.eas_group:
	# 				continue 
	# 			if self.eas_group == 'Group II' and current_date >= child.target_start_date:
	# 				active_found = True
	# 				break
	# 			if self.eas_group == 'Group I' and (child.target_start_date <= current_date <= child.target_end_date):
	# 				active_found = True
	# 				break

	# 			if not active_found:
	# 				frappe.throw(_('No active Target Setup found in EAS Calendar <b>{}</b>').format(self.eas_calendar))


	def check_duplicate_entry(self):
		# check duplicate entry for particular employee
		pass

	def check_target(self):
		

		check = frappe.db.get_value("EAS Group", self.eas_group, "required_to_set_target")
		eas_setting=frappe.frappe.get_doc('EAS Settings')
		if not check:
			frappe.throw(
					title='Error',
					msg="You are not required to set Target")
		else:
			if not self.target_item:
				frappe.throw(_('You need to <b>Set The Target</b>'))

			total_target_weightage = 0
			target = len(self.get('target_item'))
			if target > eas_setting.max_no_of_target or target < eas_setting.min_no_of_target:
				frappe.throw(
					title='Error',
					msg="Total number of target must be between <b>{}</b> and <b>{}</b> but you have set only <b>{}</b> target".format(eas_setting.min_no_of_target,eas_setting.max_no_of_target,target))
			# total weightage must be 100



			#added by kinzang.n to validate with EAS Calendar year
			eas_calendar = frappe.get_doc("EAS Calendar", self.eas_calendar)
			
			
			if not eas_calendar.fiscal_year:
				frappe.throw(
					title=_("Configuration Error"),
					msg=_("Fiscal Year is not set in EAS Calendar <b>{}</b>").format(self.eas_calendar)
				)
				
				# Get Fiscal Year date rang
			fy = frappe.get_doc("Fiscal Year", eas_calendar.fiscal_year)
			fy_start = getdate(fy.year_start_date)
			fy_end = getdate(fy.year_end_date)

			
			for i, t in enumerate(self.target_item):
				row_num = i + 1
				if not t.from_date or not t.to_date:
					frappe.throw(
						_("From Date and To Date are mandatory at Row <b>{}</b>").format(row_num)
					)
				from_date = getdate(t.from_date)
				to_date = getdate(t.to_date)
				
				# From Date must be inside EAS Calendar Fiscal Year
				if from_date < fy_start or from_date > fy_end:
					frappe.throw(
						title=_("Error"),
						msg=_(
							"<b>From Date</b> {}, must be within EAS Calendar Fiscal Year "
							"<b>{}</b> ({} to {}) at Row <b>{}</b>"
						).format(
							formatdate(from_date),
							fy.name,
							formatdate(fy_start),
							formatdate(fy_end),
							row_num
						)	
					)
				
				# To Date must be inside EAS Calendar Fiscal Year
				if to_date < fy_start or to_date > fy_end:
					frappe.throw(
						title=_("Error"),
						msg=_(
							"<b>To Date</b> {} must be within EAS Calendar Fiscal Year "
							"<b>{}</b> ({} to {}) at Row <b>{}</b>"
						).format(
							formatdate(to_date),
							fy.name,
							formatdate(fy_start),
							formatdate(fy_end),
							row_num
						)	
					)
				# From Date must be <= To Date
				if from_date > to_date:
					frappe.throw(
						title=_("Error"),
						msg=_(
							"<b>From Date</b> cannot be greater than <b>To Date</b> "
							"at Row <b>{}</b>"
						).format(row_num)
					)

			
			#till here
	


			# posting_year = getdate(self.date).year #added by kinzang to get yeear of posting date

			# for i, t in enumerate(self.target_item):
			# 	row_num = i + 1


			# 	# added by kinzang to validate the from date and to date with posting date
			# 	#frappe.throw(str("hi"))
			# 	if getdate(t.from_date).year != posting_year:
			# 		frappe.throw(
			# 			title=_("Error"),
			# 			msg=_("<b>From Date</b> cannot be less than <b>{}</b> in Target Item at Row <b>{}</b>".format(posting_year, i+1)))

			# 	if getdate(t.to_date).year != posting_year:
			# 		frappe.throw(
			# 			title=_("Error"),
			# 			msg=_("<b>To Date</b> cannot be greater than <b>{}</b> in Target Item at Row <b>{}</b>".format(posting_year ,i+1)))	
					
			# 	if getdate(t.from_date) > getdate(t.to_date):
			# 		frappe.throw(
			# 			title=_("Error"),
			# 			msg=_(" <b>From Date</b> cannot be greater than <b>To Date</b> in Target Item at Row <b>{}</b>".format(i+1))
			# 		)	

					# till here



			#their orginal code
				#frappe.throw(str("hi"))
				# if getdate(t.from_date).year < getdate().year:
				# 	frappe.throw(
				# 		title=_("Error"),
				# 		msg=_("<b>From Date</b> cannot be less than <b>{}</b> in Target Item at Row <b>{}</b>".format(getdate().year,i+1)))

				# if getdate(t.to_date).year > getdate().year:
				# 	frappe.throw(
				# 		title=_("Error"),
				# 		msg=_("<b>To Date</b> cannot be greater than <b>{}</b> in Target Item at Row <b>{}</b>".format(getdate().year,i+1)))	
					
				# if t.from_date > t.to_date:
				# 	frappe.throw(
				# 		title=_("Error"),
				# 		msg=_(" <b>From Date</b> cannot be greater than <b>To Date</b> in Target Item at Row <b>{}</b>".format(i+1)))

				
				if t.weightage < eas_setting.min_weightage_for_target:
					frappe.throw(
						title=_("Error"),
						msg=_(" min watage should grater <b>{}</b>".format(eas_setting.min_weightage_for_target,row_num)))
				if flt(t.weightage) > flt(eas_setting.max_weightage_for_target) or flt(t.weightage) < flt(eas_setting.min_weightage_for_target):
					frappe.throw(
						title=_('Error'),
						msg="Weightage for target must be between <b>{}</b> and <b>{}</b> but you have set <b>{}</b> at row <b>{}</b>".format(eas_setting.min_weightage_for_target,eas_setting.max_weightage_for_target,t.weightage, i+1))

				
				total_target_weightage += flt(t.weightage)
			
			#frappe.throw(str(eas_setting.max_rating_limit))
			if flt(total_target_weightage) !=flt(eas_setting.max_rating_limit):
				frappe.throw(
					title=_("Error"),
					msg=_('Sum of Weightage for Target must be <b>{0}</b> but your total weightage is <b>{1}</b>'.format(eas_setting.max_rating_limit,total_target_weightage)))

			self.total_weightage = total_target_weightage

	@frappe.whitelist()
	def calculate_total_weightage(self):
		total = 0
		for item in self.target_item :
			total += flt(item.weightage)
		self.total_weightage = total
	
	def set_approver_designation(self):
		desig = frappe.db.get_value('Employee', {'user_id': self.approver}, 'designation')
		return desig
 
@frappe.whitelist()
def create_review(source_name, target_doc=None):
	
	
	
	#frappe.throw(str(lattest_approver))
	if frappe.db.exists('Review', {'target':source_name, 'docstatus':('=',1)}):
		frappe.throw(
			title='Error',
			msg="You have already created Review for this Target")
		
	doclist = get_mapped_doc("Target Set Up", source_name, {
		"Target Set Up": {
			"doctype": "Review",
			"field_map":{
					"target":"name"
				},
			},
		"Performance Target Evaluation": {
				"doctype":"Review Target Item"
			},
		"Competency Item":{
			"doctype":"Review Competency Item"
		}
	}, target_doc)

	return doclist

@frappe.whitelist()
def create_evaluation(source_name, target_doc=None):
	if frappe.db.exists('Performance Evaluation',
		{'target_set_up':source_name,
			'docstatus':('!=',2)
		}):
		frappe.throw(
			title='Error',
			msg="You have already created Evaluation for this Target")
	doclist = get_mapped_doc("Target Set Up", source_name, {
		"Target Set Up": {
			"doctype": "Performance Evaluation",
			"field_map":{
					"target_set_up":"name"
				},
		},
		"Performance Target Evaluation":{
			"doctype":"Evaluate Target Item"
		},
		"Negative Target":{
			"doctype":"Performance Evaluation Negative Target"
		}

	}, target_doc)
	return doclist

@frappe.whitelist()
def manual_approval_for_hr(name, employee, eas_calendar):
	frappe.db.sql("update `tabTarget Set Up` set workflow_state = 'Approved', docstatus = 1 where employee = '{0}' and eas_calendar = '{1}' and name = '{2}' and workflow_state = 'Waiting Approval'".format(employee, eas_calendar, name))
	frappe.msgprint("Document has been Approved")

def get_permission_query_conditions(user):
	# restrict user from accessing this doctype    
	if not user: user = frappe.session.user     
	user_roles = frappe.get_roles(user)

	if user == "Administrator":      
		return
	if "HR Master" in user_roles or "HR Manager" in user_roles:       
		return
	return """(
		`tabTarget Set Up`.owner = '{user}'
		or
		exists(select 1
				from `tabEmployee`
				where `tabEmployee`.name = `tabTarget Set Up`.employee
				and `tabEmployee`.user_id = '{user}')
		or
		(`tabTarget Set Up`.approver = '{user}' and `tabTarget Set Up`.workflow_state not in ('Draft', 'Rejected','Cancelled'))
	)""".format(user=user)