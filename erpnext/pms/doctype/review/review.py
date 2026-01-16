# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
# developed by Birendra on 15/02/2021

from __future__ import unicode_literals
from frappe import _
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, nowdate, getdate, formatdate
from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states

class Review(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.pms.doctype.additional_achievements.additional_achievements import AdditionalAchievements
		from erpnext.pms.doctype.review_target_item.review_target_item import ReviewTargetItem
		from frappe.types import DF

		additional_items: DF.Table[AdditionalAchievements]
		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Data | None
		approver_name: DF.Data | None
		branch: DF.Link | None
		company: DF.Link | None
		department: DF.Link | None
		designation: DF.Link | None
		division: DF.Link | None
		eas_calendar: DF.Link
		eas_group: DF.Link | None
		employee: DF.Link
		employee_name: DF.ReadOnly | None
		end_date: DF.ReadOnly | None
		grade: DF.Link | None
		rev_workflow_state: DF.Data | None
		review_date: DF.Date | None
		review_target_item: DF.Table[ReviewTargetItem]
		section: DF.Link | None
		start_date: DF.ReadOnly | None
		target: DF.Link | None
		unit: DF.Link | None
	# end: auto-generated types
	def validate(self):
		#self.check_duplicate_entry()

		self.update_report_to()
		validate_workflow_states(self)
		if self.workflow_state != "Approved":
			notify_workflow_states(self)
		self.check_target()
		
		self.validate_calendar()
		self.validate_row_deletion()

	def before_submit(self):
		self.validate_calendar()
	

	def on_submit(self):
		pass
		# self.validate_calendar()

	def validate_row_deletion(self):
		for row in self.review_target_item:
			if row.get('delete_flag'):
				frappe.throw("Deletion of rows is not allowed.")
	
	# def validate_calendar(self): 
	# 	# check whether pms is active for review
	# 	if not frappe.db.exists("EAS Calendar",{"name": self.eas_calendar, "docstatus": 1,
	# 				"review_start_date":("<=",nowdate()),"review_end_date":(">=",nowdate())}):
	# 		frappe.throw(_('Review for EAS Calendar <b>{}</b> is not open please check your posting date').format(self.eas_calendar))
	

	# kinzang.n Added. To validate the date range from eas calendar review start date and end date. Employee can create review with eas calendar date range.
	
	def validate_calendar(self):
		if self.amended_from:
			doc = frappe.get_doc("Review", self.amended_from)
			if self.eas_calendar != doc.eas_calendar:
				frappe.throw(_("EAS Calendar does not match with the cancelled Review"))
			return
		
		# if self.workflow_state not in ["Draft", "Rejected"]:
		# 	return

		if self.docstatus == 2:
			return
		
		if not self.review_date:
			frappe.throw(_("Please select Review Date"))

		review_date = getdate(self.review_date)	
		eas_calendar = frappe.get_doc("EAS Calendar", self.eas_calendar)
		
		active_found = False
		allowed_ranges = []
		
		for item in eas_calendar.get("items", []):
			if item.eas_group != self.eas_group:
				continue
			if not item.review_start_date or not item.review_end_date:
				continue
			start_date = getdate(item.review_start_date)
			end_date = getdate(item.review_end_date)
			
			allowed_ranges.append(f"{formatdate(start_date)} to {formatdate(end_date)}")
			
			if start_date <= review_date <= end_date:
				active_found = True
				break
			
		if not allowed_ranges:
			frappe.throw(_(
				"No Review date range is defined for EAS Group <b>{}</b> in EAS Calendar <b>{}</b>."
			).format(self.eas_group, self.eas_calendar))
				
		if not active_found:
			frappe.throw(_(
				"EAS Review for <b>{group}</b> can only be created/Approve within the allowed date range(s) "
				"in EAS Calendar <b>{calendar}</b>: <b>{ranges}</b>"
			).format(
				group=self.eas_group,
				calendar=self.eas_calendar,
				ranges=", ".join(allowed_ranges)
			))

 		# till  here added bt kinzang.n



	# def check_duplicate_entry(self):
	# 	# check duplicate entry for particular employee
	# 	if self.reference and len(frappe.db.get_list('Review',filters={'employee': self.employee, 'eas_calendar': self.eas_calendar, 'docstatus': 1,'reference':self.reference})) > 2:
	# 		frappe.throw("You cannot set more than <b>2</b> Review for EAS Calendar <b>{}</b>".format(self.eas_calendar))
		
	# 	if self.reference and frappe.db.get_list('Review',filters={'employee': self.employee, 'eas_calendar': self.eas_calendar, 'docstatus': 1,'reference':self.reference,'target':self.target}):
	# 		frappe.throw("You cannot set more than <b>1</b> Review for EAS Calendar <b>{}</b> for Target <b>{}</b>".format(self.eas_calendar, self.target))

	# 	if not self.reference and frappe.db.exists("Review", {'employee': self.employee, 'eas_calendar': self.pms_calendar, 'docstatus': 1}):
	# 			frappe.throw(_('You have already set the Review for EAS Calendar <b>{}</b>'.format(self.pms_calendar)))
	def update_report_to(self):
		lattest_approver=frappe.get_value("Employee",self.employee,"reports_to")
		user_id,emp_name,deg=frappe.get_value("Employee",lattest_approver,["user_id","employee_name","designation"])
		#frappe.throw(str(user_id))
		self.approver=user_id
		self.approver_name=emp_name
		self.approver_designation=deg

	def check_target(self):
		if not frappe.db.get_value("EAS Group", self.eas_group, "required_to_set_target"):
			frappe.throw(title='Error', msg="You are not required to set Target")
		else:
			if not self.review_target_item:
				frappe.throw(_('You need to <b>Set The Target</b>'))

			#total_target_weightage = 0



			
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

			total_target_weightage = 0

			
			for i, t in enumerate(self.review_target_item):
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

				weight = flt(t.weightage or 0)
				total_target_weightage +=weight

			
			#till here



			#total weightage must be 100
			#for i, t in enumerate(self.review_target_item):
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

				
			#total_target_weightage += flt(t.weightage)

			if flt(total_target_weightage) != 100:
				frappe.throw(
					title=_("Error"),
					msg=_('Sum of Weightage for Target must be 100 but your total weightage is <b>{}</b>'.format(total_target_weightage)))

			self.total_weightage = total_target_weightage


	
 
@frappe.whitelist()
def create_evaluation(source_name, target_doc=None):

	doclist = get_mapped_doc("Review", source_name, {
		"Review": {
			"doctype": "Performance Evaluation",
			"field_map":{
					"review": "name",
				},
		},
		"Review Target Item":{
			"doctype": "Evaluate Target Item",
		},

	}, target_doc)
	return doclist

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator":
		return
	if "HR User" in user_roles or "HR Manager" in user_roles:
		return

	return """(
		`tabReview`.owner = '{user}'
		or
		exists(select 1
				from `tabEmployee`
				where `tabEmployee`.name = `tabReview`.employee
				and `tabEmployee`.user_id = '{user}')
		or
		(`tabReview`.approver = '{user}' and `tabReview`.workflow_state not in ('Draft', 'Rejected', 'Cancelled'))
	)""".format(user=user)