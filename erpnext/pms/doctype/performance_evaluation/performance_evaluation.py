# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
# developed by Birendra on 01/03/2021

from __future__ import unicode_literals
from frappe import _
import frappe
from frappe.model.document import Document
from frappe.utils import flt,nowdate, cint
from frappe.model.mapper import get_mapped_doc
from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states

class PerformanceEvaluation(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.pms.doctype.evaluate_competency_item.evaluate_competency_item import EvaluateCompetencyItem
		from erpnext.pms.doctype.evaluate_target_item.evaluate_target_item import EvaluateTargetItem
		from frappe.types import DF

		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Data | None
		approver_name: DF.Data | None
		branch: DF.Link | None
		company: DF.Link | None
		competency_score_percent: DF.Percent
		competency_self_rating: DF.Float
		competency_self_rating_percent: DF.Percent
		competency_total_weightage: DF.Percent
		cost_center: DF.Link | None
		designation: DF.Link | None
		division: DF.Link | None
		eas_calendar: DF.Link
		eas_group: DF.Link
		employee: DF.Link
		employee_name: DF.ReadOnly | None
		end_date: DF.Date | None
		eval_workflow_state: DF.Data | None
		evaluate_competency_item: DF.Table[EvaluateCompetencyItem]
		evaluate_target_item: DF.Table[EvaluateTargetItem]
		evaluation_date: DF.Date | None
		final_score_percent: DF.Percent
		grade: DF.Link | None
		overall_rating: DF.Link | None
		review: DF.Link | None
		section: DF.Link | None
		start_date: DF.Date | None
		target_score_percent: DF.Percent
		target_self_rating: DF.Float
		target_self_rating_percent: DF.Percent
		target_total_weightage: DF.Percent
	# end: auto-generated types

	def validate(self): 
		# self.check_duplicate_entry()
		# self.validate_calendar()
		self.calculate_target_score()
		self.calculate_competency_score()
		self.calculate_final_score()
		# self.check_target()
		# validate_workflow_states(self)

	def on_submit(self):
		self.validate_calendar()
		# self.create_employee_pms_record()
	
	def on_update_after_submit(self):
		self.calculate_target_score()
		self.calculate_competency_score()		
		self.calculate_final_score()
		self.update_employee_pms_record() 

	# def on_cancel(self):
	# 	self.remove_employee_pms_record()

	@frappe.whitelist()
	def create_employee_pms_record(self):
		emp = frappe.get_doc("Employee",self.employee)
		row = emp.append("employee_pms",{})
		row.fiscal_year = self.eas_calendar
		row.final_score = self.final_score
		row.final_score_percent = self.final_score_percent
		row.overall_rating = self.overall_rating
		row.reference_type = 'Performance Evaluation'
		row.performance_evaluation = self.name
		emp.save(ignore_permissions=True)

	def remove_employee_pms_record(self):
		doc = frappe.db.get_value("Employee PMS Rating", {"performance_evaluation":self.name}, "name")
		if doc:
			frappe.delete_doc("Employee PMS Rating", doc)
		else:
			frappe.msgprint("""No PMS record found in Employee Master Data of employee <a href= "#Form/Employee/{0}">{0}</a>""".format(self.employee))
	
	def update_employee_pms_record(self):
		doc = frappe.get_doc("Employee", self.employee)
		for d in doc.employee_pms:
			if d.fiscal_year == self.eas_calendar and d.performance_evaluation == self.name:
				d.final_score = self.final_score
				d.final_score_percent = self.final_score_percent
				d.overall_rating = self.overall_rating
		doc.save(ignore_permissions=True)
			
	def calculate_target_score(self):
		target_rating = frappe.db.get_value("EAS Group", self.eas_group, "weightage_for_target")
		total_self, supervisor_rating = 0.0, 0.0
		for item in self.evaluate_target_item :
			total_self 			+= flt(item.self_rating)
			supervisor_rating 	+= flt(item.supervisor_rating)

		self_percent = flt(total_self)/100 * flt(target_rating)
		sup_percent = flt(supervisor_rating)/100 * flt(target_rating)

		self.target_self_rating = total_self
		self.target_self_rating_percent = self_percent

		self.target_supervisor_rating = supervisor_rating
		self.target_score_percent = sup_percent

	def calculate_competency_score(self):
		if not self.evaluate_competency_item:
			frappe.throw('Competency cannot be empty. Please use <b>Get Competency Button</b>')

		comp_rating = frappe.db.get_value("EAS Group", self.eas_group, "weightage_for_competency")
		total_self, supervisor_rating = 0.0, 0.0
		for item in self.evaluate_competency_item:
			total_self 			+= flt(item.self_rating)
			supervisor_rating 	+= flt(item.supervisor_rating)

		self_percent = flt(total_self)/100 * flt(comp_rating)
		sup_percent = flt(supervisor_rating)/100 * flt(comp_rating)

		self.competency_self_rating = total_self
		self.competency_self_rating_percent = self_percent

		# self.competency_supervisor_rating = supervisor_rating
		self.competency_score_percent = sup_percent

	def calculate_final_score(self):
		self.target_total_weightage, self.competency_total_weightage = frappe.db.get_value("EAS Group", {"name":self.eas_group}, ["weightage_for_target", "weightage_for_competency"])

		self.db_set('final_score_percent', (flt(self.target_score_percent) + flt(self.competency_score_percent)))

		overall_rating = frappe.db.sql('''select name from `tabOverall Rating` where  upper_range_percent >= {0} and lower_range_percent <= {0}'''.format(self.final_score_percent))

		if len(overall_rating) > 0:
			self.overall_rating = overall_rating[0][0]
		self.db_set('overall_rating', self.overall_rating)
			
	def validate_calendar(self):
		if not frappe.db.exists("PMS Calendar", {"name": self.eas_calendar, "docstatus": 1, "evaluation_start_date": ("<=", nowdate()), "evaluation_end_date": (">=", nowdate())}):
			frappe.throw(
				_('Evaluation for EAS Calendar <b>{}</b> is not open, Check the posting date').format(self.eas_calendar))

	def check_duplicate_entry(self):
		if self.reference and len(frappe.db.get_list('Performance Evaluation',filters={'employee': self.employee, 'eas_calendar': self.eas_calendar, 'docstatus': 1,'reference':self.reference})) > 2:
			frappe.throw("You cannot set more than <b>2</b> Evaluation for PMS Calendar <b>{}</b>".format(self.eas_calendar))
		
		if self.reference and frappe.db.get_list('Performance Evaluation',filters={'employee': self.employee, 'eas_calendar': self.eas_calendar, 'docstatus': 1,'reference':self.reference,'review':self.review}):
			frappe.throw("You cannot set more than <b>1</b> Performance Evaluation for PMS Calendar <b>{}</b> for Review <b>{}</b>".format(self.eas_calendar, self.review))

		if not self.reference and frappe.db.exists("Performance Evaluation", {'employee': self.employee, 'eas_calendar': self.eas_calendar, 'docstatus': 1}):
			frappe.throw(_('Evaluation for employee <b>{}</b> has been already approved for PMS Calendar <b>{}</b>'.format(self.employee_name, self.eas_calendar)), title="Duplicate Entry")

	@frappe.whitelist()
	def get_competency(self):
		self.set('evaluate_competency_item', [])
		
		data = frappe.db.sql("""
			SELECT 
				name AS parent, 
				competency, 
				weightage,
				description
			FROM 
				`tabWork Competency`
			WHERE eas_group = %(eas_group)s
		""", {"eas_group": self.eas_group}, as_dict=True)

		if not data:
			frappe.throw(_('There are no Work Competencies defined'))

		if data:
			for row in data:
				self.append('evaluate_competency_item', row)
			frappe.msgprint(_('Competencies have been added successfully'))

@frappe.whitelist()
def pms_appeal(source_name, target_doc=None):
	if frappe.db.exists('PMS Appeal',
		{'reference':source_name,
		'docstatus':('!=',2)
		}):
		frappe.throw(
			title='Error',
			msg="You have already created PMS Appeal for this Evaluation")
	doclist = get_mapped_doc("Performance Evaluation",
		source_name, 
		{
		"Performance Evaluation": {
			"doctype": "PMS Appeal",
			"field_map":{
					"reference_name":"name",
				},
		},
		"Evaluate Target Item":{
			"doctype":"Evaluate Target Item"
		},
		"Evaluate Competency":{
			"doctype":"Evaluate Competency"
		},
		"Leadership Competency":{
			"doctype":"Leadership Competency"
		}
	}, target_doc)

	return doclist

def get_permission_query_conditions(user):
	# restrict user from accessing this doctype
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator":
		return
	if "HR User" in user_roles or "HR Manager" in user_roles:
		return

	return """(
		`tabPerformance Evaluation`.owner = '{user}'
		or
		exists(select 1
				from `tabEmployee`
				where `tabEmployee`.name = `tabPerformance Evaluation`.employee
				and `tabEmployee`.user_id = '{user}')
		or
		(`tabPerformance Evaluation`.approver = '{user}' and `tabPerformance Evaluation`.eval_workflow_state not in ('Draft', 'Rejected', 'Cancelled'))
		)""".format(user=user)

