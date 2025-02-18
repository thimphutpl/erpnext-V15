# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
# developed by Birendra on 15/02/2021

from __future__ import unicode_literals
from frappe import _
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, nowdate, getdate
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
		# self.check_duplicate_entry()
		# validate_workflow_states(self)
		# if self.workflow_state != "Approved":
		# 	notify_workflow_states(self)
		# self.check_target()
		
		# self.validate_calendar()
		self.validate_row_deletion()

	def on_submit(self):
		pass
		# self.validate_calendar()

	def validate_row_deletion(self):
		for row in self.review_target_item:
			if row.get('delete_flag'):
				frappe.throw("Deletion of rows is not allowed.")
	
	def validate_calendar(self): 
		# check whether pms is active for review
		if not frappe.db.exists("EAS Calendar",{"name": self.eas_calendar, "docstatus": 1,
					"review_start_date":("<=",nowdate()),"review_end_date":(">=",nowdate())}):
			frappe.throw(_('Review for EAS Calendar <b>{}</b> is not open please check your posting date').format(self.eas_calendar))

	# def check_duplicate_entry(self):
	# 	# check duplicate entry for particular employee
	# 	if self.reference and len(frappe.db.get_list('Review',filters={'employee': self.employee, 'eas_calendar': self.eas_calendar, 'docstatus': 1,'reference':self.reference})) > 2:
	# 		frappe.throw("You cannot set more than <b>2</b> Review for EAS Calendar <b>{}</b>".format(self.eas_calendar))
		
	# 	if self.reference and frappe.db.get_list('Review',filters={'employee': self.employee, 'eas_calendar': self.eas_calendar, 'docstatus': 1,'reference':self.reference,'target':self.target}):
	# 		frappe.throw("You cannot set more than <b>1</b> Review for EAS Calendar <b>{}</b> for Target <b>{}</b>".format(self.eas_calendar, self.target))

	# 	if not self.reference and frappe.db.exists("Review", {'employee': self.employee, 'eas_calendar': self.pms_calendar, 'docstatus': 1}):
	# 			frappe.throw(_('You have already set the Review for EAS Calendar <b>{}</b>'.format(self.pms_calendar)))

	def check_target(self):
		if not frappe.db.get_value("EAS Group", self.eas_group, "required_to_set_target"):
			frappe.throw(title='Error', msg="You are not required to set Target")
		else:
			if not self.review_target_item:
				frappe.throw(_('You need to <b>Set The Target</b>'))

			total_target_weightage = 0
			# total weightage must be 100
			for i, t in enumerate(self.review_target_item):
				if getdate(t.from_date).year < getdate().year:
					frappe.throw(
						title=_("Error"),
						msg=_("<b>From Date</b> cannot be less than <b>{}</b> in Target Item at Row <b>{}</b>".format(getdate().year,i+1)))

				if getdate(t.to_date).year > getdate().year:
					frappe.throw(
						title=_("Error"),
						msg=_("<b>To Date</b> cannot be greater than <b>{}</b> in Target Item at Row <b>{}</b>".format(getdate().year,i+1)))	
					
				if t.from_date > t.to_date:
					frappe.throw(
						title=_("Error"),
						msg=_(" <b>From Date</b> cannot be greater than <b>To Date</b> in Target Item at Row <b>{}</b>".format(i+1)))
				
				total_target_weightage += flt(t.weightage)

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