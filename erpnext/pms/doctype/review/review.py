# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, nowdate
from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states

class Review(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.pms.doctype.additional_achievements.additional_achievements import AdditionalAchievements
		from erpnext.pms.doctype.negative_target_review.negative_target_review import NegativeTargetReview
		from erpnext.pms.doctype.review_competency_item.review_competency_item import ReviewCompetencyItem
		from erpnext.pms.doctype.review_target_item.review_target_item import ReviewTargetItem
		from frappe.types import DF

		additional_items: DF.Table[AdditionalAchievements]
		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Data | None
		approver_name: DF.Data | None
		branch: DF.Link | None
		business_target: DF.Table[NegativeTargetReview]
		company: DF.Link | None
		department: DF.Link | None
		designation: DF.Link | None
		division: DF.Link | None
		employee: DF.Link
		employee_name: DF.ReadOnly | None
		end_date: DF.ReadOnly | None
		grade: DF.Link | None
		max_no_of_target: DF.Float
		max_weightage_for_target: DF.Float
		min_no_of_target: DF.Float
		min_weightage_for_target: DF.Float
		negative_target: DF.Check
		old_employee_id: DF.Data | None
		pms_calendar: DF.Link
		pms_group: DF.Link | None
		reason: DF.SmallText | None
		reference: DF.Link | None
		region: DF.Link | None
		required_to_set_target: DF.Data | None
		rev_workflow_state: DF.Data | None
		review_competency_item: DF.Table[ReviewCompetencyItem]
		review_date: DF.Date | None
		review_target_item: DF.Table[ReviewTargetItem]
		review_type: DF.Literal["Review I", "Review II", "Review III", "Review IV"]
		section: DF.Link | None
		set_manual_approver: DF.Check
		start_date: DF.ReadOnly | None
		target: DF.Link | None
		total_weightage: DF.Float
		unit: DF.Link | None
		user_id: DF.Link | None
	# end: auto-generated types
	def validate(self):
		self.check_duplicate_entry()
		validate_workflow_states(self)
		if self.workflow_state != "Approved":
			notify_workflow_states(self)
		self.check_target()

	def on_submit(self):
		if self.reference and self.reason:
			return
		else:
			self.validate_calendar()
	
	def validate_calendar(self): 
		# check whether pms is active for review
		# map, review type and quarterly review start date and end date fields
		review_date = [
			{"review_type":"Review I", "start_date":"review_start_date", "end_date":"review_end_date"},
			{"review_type":"Review II", "start_date":"review_ii_start_date", "end_date":"review_ii_end_date"},
			{"review_type":"Review III", "start_date":"review_iii_start_date", "end_date":"review_iii_end_date"},
			{"review_type":"Review IV", "start_date":"review_iV_start_date", "end_date":"review_iV_end_date"}
		]
		for d in review_date:
			if d.get('review_type') == self.review_type and not frappe.db.exists("PMS Calendar",{"name": self.pms_calendar,"docstatus": 1,
						d.get("start_date"):("<=",nowdate()),d.get("end_date"):(">=",nowdate())}):
				frappe.throw(_('Review for PMS Calendar <b>{}</b> and {} is not open please check your posting date').format(self.pms_calendar, self.review_type))

	def check_duplicate_entry(self):       
		# check duplicate entry for particular employee
		if self.reference and len(frappe.db.get_list('Review',filters={'employee': self.employee, 'pms_calendar': self.pms_calendar, 'docstatus': 1,'reference':self.reference})) > 4:
			frappe.throw("You cannot set more than <b>4</b> Review for PMS Calendar <b>{}</b>".format(self.pms_calendar))
		
		if self.reference and frappe.db.get_list('Review',filters={'employee': self.employee, 'pms_calendar': self.pms_calendar, 'docstatus': 1,'reference':self.reference,'target':self.target, 'review_type': self.review_type}):
			frappe.throw("You cannot set more than <b>1</b> Review for PMS Calendar <b>{}</b> and Review Type <b>{}</b> for Target <b>{}</b>".format(self.pms_calendar, self.review_type, self.target))

		if not self.reference and frappe.db.exists("Review", {'employee': self.employee, 'pms_calendar': self.pms_calendar, 'docstatus': 1, 'review_type': self.review_type}):
				frappe.throw(_('You have already set the Review for PMS Calendar <b>{}</b>'.format(self.pms_calendar)))

	def check_target(self):
		check = frappe.db.get_value("PMS Group",self.pms_group,"required_to_set_target")
		if not check:
			frappe.throw(
					title='Error',
					msg="You are not required to set Target")
		else:
			if not self.review_target_item:
				frappe.throw(_('You need to <b>Set The Target</b>'))

			# validate total number of target
			target_length = flt(len(self.review_target_item))
			if flt(target_length) > flt(self.max_no_of_target) or flt(target_length) < flt(self.min_no_of_target):
				frappe.throw(
					title='Error',
					msg="Total number of target must be between <b>{}</b> and <b>{}</b> but you have set only <b>{}</b> target".format(self.min_no_of_target,self.max_no_of_target,target_length))

			total_target_weightage = 0
			# total weightage must be 100
			for i, t in enumerate(self.review_target_item):
				if t.qty_quality == 'Quantity' and flt(t.quantity) <= 0 :
					frappe.throw(
						title=_('Error'),
						msg=_("<b>{}</b> value is not allowed for <b>Quantity</b> in Target Item at Row <b>{}</b>".format(t.quantity,i+1)))

				if t.qty_quality == 'Quality' and flt(t.quality) <= 0 :
					frappe.throw(
						title=_("Error"),
						msg=_("<b>{}</b> value is not allowed for <b>Quality</b> in Target Item at Row <b>{}</b>".format(t.quality,i+1)))

				if flt(t.weightage) > flt(self.max_weightage_for_target) or flt(t.weightage) < flt(self.min_weightage_for_target):
					frappe.throw(
						title=_('Error'),
						msg="Weightage for target must be between <b>{}</b> and <b>{}</b> but you have set <b>{}</b> at row <b>{}</b>".format(self.min_weightage_for_target,self.max_weightage_for_target,t.weightage, i+1))

				if flt(t.timeline) <= 0:
					frappe.throw(
						title=_("Error"),
						msg=_("<b>{}</b> value is not allowed for <b>Timeline</b> in Target Item at Row <b>{}</b>".format(t.timeline,i+1)))
				
				total_target_weightage += flt(t.weightage)
				if t.qty_quality == 'Quantity':
					t.quality = None

				if t.qty_quality == 'Quality':
					t.quantity = None

			if flt(total_target_weightage) != 100:
				frappe.throw(
					title=_("Error"),
					msg=_('Sum of Weightage for Target must be 100 but your total weightage is <b>{}</b>'.format(total_target_weightage)))

			self.total_weightage = total_target_weightage

	def set_approver_designation(self):
		desig = frappe.db.get_value('Employee', {'user_id': self.approver}, 'designation')
		return desig
 
@frappe.whitelist()
def create_evaluation(source_name, target_doc=None):
	if frappe.db.exists('Performance Evaluation',
		{'review':source_name,
		'docstatus':('!=',2)
		}):
		frappe.throw(
			title='Error',
			msg="You have already created Evaluation for this Target")
	doclist = get_mapped_doc("Review", source_name, {
		"Review": {
			"doctype": "Performance Evaluation",
			"field_map":{
					"review":"name"
				},
		},
		"Review Target Item":{
			"doctype":"Evaluate Target Item"
		},
		"Negative Target Review":{
			"doctype":"Performance Evaluation Negative Target"
		}
	}, target_doc)

	return doclist

@frappe.whitelist()
def create_review(source_name, target_doc=None):
	review_level = frappe.flags.args.review_level
	if frappe.db.exists('Review',
		{'target':frappe.flags.args.target_id,
		'review_type':review_level,
		'docstatus':('!=',2)
		}):
		frappe.throw(
			title='Error',
			msg="You have already created Review for "+ str(review_level) )

	def update_item(obj, target, source_parent):
		target.review_type = review_level

	doclist = get_mapped_doc("Review", source_name, {
		"Review": {
			"doctype": "Review",
			"postprocess": update_item
			},
		"Review Target Item":{
				"doctype":"Review Target Item"
			},
		"Additional Achievements":{
				"doctype":"Additional Achievements"
			},
		"Negative Target Review":{
			"doctype":"Negative Target Review"
			},
	}, target_doc)

	return doclist

@frappe.whitelist()
def manual_approval_for_hr(name, employee, pms_calendar):
	frappe.db.sql("update `tabReview` set rev_workflow_state = 'Approved', docstatus = 1 where employee = '{0}' and pms_calendar = '{1}' and name = '{2}' and rev_workflow_state = 'Waiting Approval'".format(employee, pms_calendar, name))
	frappe.msgprint("Document has been Approved")

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
