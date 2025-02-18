# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import urllib.parse
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate, getdate
from frappe.model.mapper import get_mapped_doc
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
		# validate_workflow_states(self) 
		# self.validate_calendar()
			
	def on_submit(self):
		return
		self.validate_calendar()

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
		
	def validate_calendar(self):
		if frappe.db.exists("Target Set Up", {"employee": self.employee, "docstatus":2, "eas_calendar": self.eas_calendar}):
			doc = frappe.get_doc('Target Set Up', self.amended_from)
			if self.eas_calendar == doc.eas_calendar:
				return
			else:
				frappe.throw(_("EAS Calendar doesnot match with the cancelled Target"))

		elif self.workflow_state == 'Draft' or self.workflow_state == 'Rejected':
			return   
		# check whether eas is active for target setup       
		elif not frappe.db.exists("EAS Calendar", {"name": self.eas_calendar, "docstatus": 1,
					"target_start_date":("<=",nowdate()), "target_end_date": (">=",nowdate())}):
			frappe.throw(_('Target Set Up for EAS Calendar <b>{}</b> is not open').format(self.eas_calendar))

	def check_duplicate_entry(self):
		# check duplicate entry for particular employee
		pass

	def check_target(self):
		check = frappe.db.get_value("EAS Group", self.eas_group, "required_to_set_target")
		if not check:
			frappe.throw(
					title='Error',
					msg="You are not required to set Target")
		else:
			if not self.target_item:
				frappe.throw(_('You need to <b>Set The Target</b>'))

			total_target_weightage = 0
			# total weightage must be 100
			for i, t in enumerate(self.target_item):
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
					msg=_('Sum of Weightage for Target must be <b>100</b> but your total weightage is <b>{}</b>'.format(total_target_weightage)))

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