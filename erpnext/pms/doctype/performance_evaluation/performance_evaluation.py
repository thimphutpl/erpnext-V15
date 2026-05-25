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
		competency_score_reviewer: DF.Percent
		competency_self_rating: DF.Float
		competency_self_rating_percent: DF.Percent
		competency_total_weightage: DF.Percent
		competency_weightage: DF.Percent
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
		reviewer: DF.Link | None
		reviewer_designation: DF.Data | None
		reviewer_name: DF.Data | None
		reviewer_weightage: DF.Percent
		section: DF.Link | None
		start_date: DF.Date | None
		target_score: DF.Percent
		target_score_percent: DF.Percent
		target_self_rating: DF.Float
		target_self_rating_percent: DF.Percent
		target_total_weightage: DF.Percent
	# end: auto-generated types

	def validate(self): 
		# self.check_duplicate_entry()
		# self.validate_calendar()
		
		#self.update_report_to()
		self.calculate_target_score()
		self.calculate_competency_score()
		self.calculate_final_score()
		self.validate_rating_permissions()
		# self.check_target()
		self.validate_workflow_permissions()


	def before_save(self):
		self.update_approver_and_reviewer()	

	#def on_submit(self):
		#self.validate_calendar()
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
			
	# def calculate_target_score(self):
	# 	target_rating = frappe.db.get_value("EAS Group", self.eas_group, "weightage_for_target")
	# 	total_self, supervisor_rating = 0.0, 0.0
	# 	for item in self.evaluate_target_item :
	# 		total_self 			+= flt(item.self_rating)
	# 		supervisor_rating 	+= flt(item.supervisor_rating)

	# 	self_percent = flt(total_self)/100 * flt(target_rating)
	# 	sup_percent = flt(supervisor_rating)/100 * flt(target_rating)

	# 	self.target_self_rating = total_self
	# 	self.target_self_rating_percent = self_percent

	# 	self.target_supervisor_rating = supervisor_rating
	# 	self.target_score_percent = sup_percent
	# 



	#added by kinzang.n to prevent to edit 
	def validate_rating_permissions(self):
		user = frappe.session.user
		
		# if new doc, skip
		if self.get("__islocal"):
			return
		# if deleted/cancelled, skip
		if not frappe.db.exists("Performance Evaluation", self.name):
			return
		
		existing = frappe.get_doc("Performance Evaluation", self.name)

		def is_changed(fieldname, row, existing_row):
			return getattr(row, fieldname) != getattr(existing_row, fieldname)
		
		def get_row_info(row, row_type):
			name = row.target if row_type == "Target" else row.competency
			return f"{row_type} ({name})"
		
		# create a map by row name to compare correctly
		existing_target_map = {r.name: r for r in existing.evaluate_target_item}
		existing_comp_map = {r.name: r for r in existing.evaluate_competency_item}
		
		# Employee editing
		if user == frappe.get_value("Employee", self.employee, "user_id"):
			
			for row in self.evaluate_target_item:
				if row.name in existing_target_map and (
					is_changed("supervisor_rating", row, existing_target_map[row.name]) or
					is_changed("reviewer_rating", row, existing_target_map[row.name]) or
					is_changed("supervisor_remarks", row, existing_target_map[row.name]) or
					is_changed("reviewer_remarks", row, existing_target_map[row.name])
				):
					frappe.throw(_(
						f"You are not allowed to edit supervisor/reviewer fields in {get_row_info(row, 'Target')}"
					))
					
			for row in self.evaluate_competency_item:
				if row.name in existing_comp_map and (
					is_changed("supervisor_rating", row, existing_comp_map[row.name]) or
					is_changed("reviewer_rating", row, existing_comp_map[row.name]) or
					is_changed("supervisor_remarks", row, existing_comp_map[row.name]) or
					is_changed("reviewer_remarks", row, existing_comp_map[row.name])
				):
					frappe.throw(_(
						f"You are not allowed to edit supervisor/reviewer fields in {get_row_info(row, 'Competency')}"
					))
		# Supervisor editing
		elif user == self.approver:
			
			for row in self.evaluate_target_item:
				if row.name in existing_target_map and (
					is_changed("reviewer_rating", row, existing_target_map[row.name]) or
					is_changed("reviewer_remarks", row, existing_target_map[row.name])
				):
					
					frappe.throw(_(
						f"Only Reviewer can edit reviewer fields in {get_row_info(row, 'Target')}"
					))
			
			for row in self.evaluate_competency_item:
				if row.name in existing_comp_map and (
					is_changed("reviewer_rating", row, existing_comp_map[row.name]) or
					is_changed("reviewer_remarks", row, existing_comp_map[row.name])
				):
					frappe.throw(_(
						f"Only Reviewer can edit reviewer fields in {get_row_info(row, 'Competency')}"
					))
		
		# Reviewer editing
		# 
		elif user == self.reviewer:
			for row in self.evaluate_target_item:
				if row.name in existing_target_map and (
					is_changed("supervisor_rating", row, existing_target_map[row.name]) or
					is_changed("supervisor_remarks", row, existing_target_map[row.name])
				):
					frappe.throw(_(
						f"Only Supervisor can edit supervisor fields in {get_row_info(row, 'Target')}"
					))
				
			for row in self.evaluate_competency_item:
				if row.name in existing_comp_map and (
					is_changed("supervisor_rating", row, existing_comp_map[row.name]) or
					is_changed("supervisor_remarks", row, existing_comp_map[row.name])
				):
					frappe.throw(_(
						f"Only Supervisor can edit supervisor fields in {get_row_info(row, 'Competency')}"
					))
		# Others
		else:
			if "Admin" not in frappe.get_roles(user):
				frappe.throw(_("You are not allowed to edit this document."))

	#till here





	# added by kinzang.n to calculate tartget score
	
	def calculate_target_score(self):
		total_self, total_supervisor, total_reviewer = 0.0, 0.0, 0.0
		
		for i, item in enumerate(self.evaluate_target_item, start=1):  # Row number starts at 1
			row_weightage = flt(item.weightage)

        	# Validate self_rating
			if flt(item.self_rating) > row_weightage:
				frappe.throw(_("Row {0}: Self Rating ({1}) cannot exceed allocated weightage ({2})").format(
					i, flt(item.self_rating), row_weightage
				))
			
			# Validate supervisor_rating
			
			if flt(item.supervisor_rating) > row_weightage:
				frappe.throw(_("Row {0}: Supervisor Rating ({1}) cannot exceed allocated weightage ({2})").format(
					i, flt(item.supervisor_rating), row_weightage
				))

			# Validate reviewer_rating
			
			if flt(item.reviewer_rating) > row_weightage:
				frappe.throw(_("Row {0}: Reviewer Rating ({1}) cannot exceed allocated weightage ({2})").format(
					i, flt(item.reviewer_rating), row_weightage
				))
				
			
			# Add to totals
			total_self += flt(item.self_rating)
			total_supervisor += flt(item.supervisor_rating)
			total_reviewer += flt(item.reviewer_rating)
		
		# Calculate percentages relative to total weightage
		total_weightage = sum(flt(item.weightage) for item in self.evaluate_target_item)
		#self_percent = (total_self / total_weightage) * 100 if total_weightage else 0
		self_percent = total_weightage
		# Assign values to parent document
		self.target_self_rating = total_self
		self.target_self_rating_percent = self_percent


		target_total_weightage = frappe.db.get_value("EAS Group", {"name":self.eas_group}, ["weightage_for_target"])

		sup_percent = (total_supervisor / 100) * target_total_weightage if total_weightage else 0
		#sup_percent = (total_supervisor / target_total_weightage) * 100 if target_total_weightage else 0
		revi_percent = (total_reviewer / 100 ) * target_total_weightage if total_weightage else 0 #added by kinzang.n
		
		# Assign values to parent document
		self.target_self_rating = total_self
		self.target_self_rating_percent = self_percent



		self.target_supervisor_rating = total_supervisor
		self.target_score_percent = sup_percent

		self.target_reviewer_rating = total_reviewer
		self.target_score = revi_percent


		#till here added by Kinzang.n



	#added by kinzang to calculate competency score
	def calculate_competency_score(self):
		if not self.evaluate_competency_item:
			frappe.throw('Competency cannot be empty. Please use <b>Get Competency Button</b>')
		
		total_self, total_supervisor, total_reviewer = 0.0, 0.0, 0.0
		
		for i, item in enumerate(self.evaluate_competency_item, start=1):
			row_weightage = flt(item.weightage)
			
			# Validate self_rating
			if flt(item.self_rating) > row_weightage:
				frappe.throw(_("Row {0}: Self Rating ({1}) cannot exceed allocated weightage ({2})").format(
					i, flt(item.self_rating), row_weightage
				))
			
			# Validate supervisor_rating
			if flt(item.supervisor_rating) > row_weightage:
				frappe.throw(_("Row {0}: Supervisor Rating ({1}) cannot exceed allocated weightage ({2})").format(
					i, flt(item.supervisor_rating), row_weightage
				))

			# Validate supervisor_rating
			if flt(item.reviewer_rating) > row_weightage:
				frappe.throw(_("Row {0}: Reviewer Rating ({1}) cannot exceed allocated weightage ({2})").format(
					i, flt(item.reviewer_rating), row_weightage
				))
				
			
			total_self += flt(item.self_rating)
			total_supervisor += flt(item.supervisor_rating)
			total_reviewer += flt(item.reviewer_rating)
		
		# Calculate percentages based on total weightage
		total_weightage = sum(flt(item.weightage) for item in self.evaluate_competency_item)
		self_percent = total_weightage
		#self_percent = (total_self / total_weightage) * 100 if total_weightage else 0

		#competency_weightage = frappe.db.get_value("EAS Group", {"name":self.eas_group}, ["weightage_for_competency"])

		#sup_percent = (total_supervisor / 100) * competency_weightage if total_weightage else 0
		#sup_percent = (total_supervisor / target_total_weightage) * 100 if target_total_weightage else 0
		#revi_percent = (total_reviewer / 100) * competency_weightage if total_weightage else 0 #added by kinzang.n
		
		#sup_percent = (total_supervisor / total_weightage) * 100 if total_weightage else 0
		# #sup_percent = total_supervisor if total_weightage else 0
		#revi_percent = (total_reviewer /total_weightage) * 100 if total_weightage else 0

		sup_percent = total_supervisor
		revi_percent = total_reviewer
		
		# Assign values to parent document
		self.competency_self_rating = total_self
		self.competency_self_rating_percent = self_percent
		#self.competency_score_percent = sup_percent
		self.competency_score_percent = sup_percent
		self.competency_score_reviewer = revi_percent

		#till here added by kinzang.n, CDCL.




	def calculate_final_score(self):
		self.target_total_weightage, self.competency_total_weightage = frappe.db.get_value("EAS Group", {"name":self.eas_group}, ["weightage_for_target", "weightage_for_competency"])

		self.reviewer_weightage, self.competency_weightage = frappe.db.get_value("EAS Group", {"name":self.eas_group}, ["weightage_for_target", "weightage_for_competency"])


		self.db_set('final_score_percent', (flt(self.target_score) + flt(self.competency_score_reviewer)))
		

		overall_rating = frappe.db.sql('''select name from `tabOverall Rating` where  upper_range_percent >= {0} and lower_range_percent <= {0}'''.format(self.final_score_percent))

		if len(overall_rating) > 0:
			self.overall_rating = overall_rating[0][0]
		self.db_set('overall_rating', self.overall_rating)



	# def calculate_competency_score(self):
	# 	if not self.evaluate_competency_item:
	# 		frappe.throw('Competency cannot be empty. Please use <b>Get Competency Button</b>')

	# 	comp_rating = frappe.db.get_value("EAS Group", self.eas_group, "weightage_for_competency")
	# 	total_self, supervisor_rating = 0.0, 0.0
	# 	for item in self.evaluate_competency_item:
	# 		total_self 			+= flt(item.self_rating)
	# 		supervisor_rating 	+= flt(item.supervisor_rating)

	# 	self_percent = flt(total_self)/100 * flt(comp_rating)
	# 	sup_percent = flt(supervisor_rating)/100 * flt(comp_rating)

	# 	self.competency_self_rating = total_self
	# 	self.competency_self_rating_percent = self_percent

	# 	# self.competency_supervisor_rating = supervisor_rating
	# 	self.competency_score_percent = sup_percent
	
	
	def update_approver_and_reviewer(self):
		if not self.employee:
			return
			
		# Employee
		emp = frappe.get_doc("Employee", self.employee)
		
		if not emp.reports_to:
			
			return
			
		# Supervisor (Approver)
		
		supervisor = frappe.get_doc("Employee", emp.reports_to)
		self.approver = supervisor.user_id
		self.approver_name = supervisor.employee_name
		self.approver_designation = supervisor.designation
		
		# Reviewer logic
		# If supervisor has reports_to → reviewer = supervisor's supervisor
		# Else → reviewer = supervisor
		reviewer_emp_name = supervisor.reports_to or supervisor.name
		reviewer = frappe.get_doc("Employee", reviewer_emp_name)
		
		self.reviewer = reviewer.user_id
		self.reviewer_name = reviewer.employee_name
		self.reviewer_designation = reviewer.designation



	
	




	# def update_report_to(self):
	# 	lattest_approver=frappe.get_value("Employee",self.employee,"reports_to")
	# 	user_id,emp_name,deg=frappe.get_value("Employee",lattest_approver,["user_id","employee_name","designation"])
	# 	#frappe.throw(str(user_id))
	# 	self.approver=user_id
	# 	self.approver_name=emp_name
	# 	self.approver_designation=deg
	
	
	# def update_reviewer_to(self):
	# 	emp = frappe.get_doc("Employee", self.employee)
		
	# 	if not emp.reports_to:
	# 		return
		
	# 	supervisor = frappe.get_doc("Employee", emp.reports_to)
	# 	reviewer_name = supervisor.reports_to or supervisor.name
	# 	reviewer = frappe.get_doc("Employee", reviewer_name)
		
	# 	self.reviewer = reviewer.user_id
	# 	self.reviewer_name = reviewer.employee_name
	# 	self.reviewer_designation = reviewer.designation





			
	# def validate_calendar(self):
	# 	if not frappe.db.exists("PMS Calendar", {"name": self.eas_calendar, "docstatus": 1, "evaluation_start_date": ("<=", nowdate()), "evaluation_end_date": (">=", nowdate())}):
	# 		frappe.throw(
	# 			_('Evaluation for EAS Calendar <b>{}</b> is not open, Check the posting date').format(self.eas_calendar))

	def check_duplicate_entry(self):
		if self.reference and len(frappe.db.get_list('Performance Evaluation',filters={'employee': self.employee, 'eas_calendar': self.eas_calendar, 'docstatus': 1,'reference':self.reference})) > 2:
			frappe.throw("You cannot set more than <b>2</b> Evaluation for PMS Calendar <b>{}</b>".format(self.eas_calendar))
		
		if self.reference and frappe.db.get_list('Performance Evaluation',filters={'employee': self.employee, 'eas_calendar': self.eas_calendar, 'docstatus': 1,'reference':self.reference,'review':self.review}):
			frappe.throw("You cannot set more than <b>1</b> Performance Evaluation for PMS Calendar <b>{}</b> for Review <b>{}</b>".format(self.eas_calendar, self.review))

		if not self.reference and frappe.db.exists("Performance Evaluation", {'employee': self.employee, 'eas_calendar': self.eas_calendar, 'docstatus': 1}):
			frappe.throw(_('Evaluation for employee <b>{}</b> has been already approved for PMS Calendar <b>{}</b>'.format(self.employee_name, self.eas_calendar)), title="Duplicate Entry")




	#added by kinzang.n .
	def validate_workflow_permissions(self):
		user = frappe.session.user

		employee_user = frappe.get_value("Employee", self.employee, "user_id")
		employee_name = self.employee_name
		
		approver_user = self.approver
		reviewer_user = self.reviewer
		
		approver_name = frappe.get_value(
			"Employee", {"user_id": approver_user}, "employee_name"
		) or approver_user
		
		reviewer_name = frappe.get_value(
			"Employee", {"user_id": reviewer_user}, "employee_name"
		) or reviewer_user
		
		previous = None
		if not self.is_new():
			previous = frappe.get_doc(self.doctype, self.name)
			
		# -------------------------------------------------
		# APPLY (Draft / Rejected → Waiting Supervisor)
		# ONLY Employee
		# -------------------------------------------------
		if previous and previous.workflow_state in ["Draft", "Rejected"] \
			and self.workflow_state == "Waiting Supervisor Approval":
			
			if user != employee_user:
				frappe.throw(
					_("Only {0} (Employee) can apply this document.")
				.format(employee_name)
			)
				
		# -------------------------------------------------
		# SUPERVISOR FORWARD
		# -------------------------------------------------
		if previous and previous.workflow_state == "Waiting Supervisor Approval" \
			and self.workflow_state == "Waiting Reviewer Approval":
			
			if user != approver_user:
				frappe.throw(
					_("Only {0} (Supervisor) can forward this document.")
					.format(approver_name)
				)
				
		# -------------------------------------------------
		# REVIEWER APPROVE
		# -------------------------------------------------
		if previous and previous.workflow_state == "Waiting Reviewer Approval" \
			and self.workflow_state == "Approved":
			
			if user != reviewer_user:
				frappe.throw(
                _("Only {0} (Reviewer) can approve this document.")
                .format(reviewer_name)
            )
				
		# -------------------------------------------------
		# EDIT / SAVE RESTRICTIONS (no state change)
		# -------------------------------------------------
		if previous and previous.workflow_state == self.workflow_state:
			
			if self.workflow_state in ["Draft", "Rejected"] and user != employee_user:
				frappe.throw(
					_("Only {0} (Employee) can edit this document.")
					.format(employee_name)
				)

			if self.workflow_state == "Waiting Supervisor Approval" and user != approver_user:
				frappe.throw(
					_("Only {0} (Supervisor) can edit this document.")
					.format(approver_name)
				)
			
			if self.workflow_state == "Waiting Reviewer Approval" and user != reviewer_user:
				frappe.throw(
					_("Only {0} (Reviewer) can edit this document.")
					.format(reviewer_name)
				)

		#till here




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
	if frappe.db.exists('EAS Appeal',
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
			"doctype": "EAS Appeal",
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
	#frappe.throw(str(user))
	if user == "Administrator":
		return
	

	#added by Kinzang.n to restrict seeing
	if "GM" in user_roles or "HR Manager" in user_roles or "CEO" in user_roles or "EAS Readonly User" in user_roles:
		assign_branch = frappe.db.get_value(
			"Assign Branch",
			{"user": user},
			"name"
		)

		if assign_branch:
			branches = frappe.get_all(
				"Branch Item",
				filters={"parent": assign_branch},
				fields=["branch"]
			)

			branch_list = [b.branch for b in branches]

			if branch_list:
				branch_condition = "', '".join(branch_list)
				return (
					"`tabPerformance Evaluation`.branch IN ('{0}')"
					.format(branch_condition)
				)

		# HR user without assigned branch → see nothing
		return "`tabPerformance Evaluation`.name = ''"
       

	return """(
		`tabPerformance Evaluation`.owner = '{user}'
		or
		exists(select 1
				from `tabEmployee`
				where `tabEmployee`.name = `tabPerformance Evaluation`.employee
				and `tabEmployee`.user_id = '{user}')
		or
		(`tabPerformance Evaluation`.approver = '{user}' and `tabPerformance Evaluation`.workflow_state not in ('Draft', 'Rejected', 'Cancelled'))
		or
		(
        	`tabPerformance Evaluation`.reviewer = '{user}'
        	and `tabPerformance Evaluation`.workflow_state not in ('Draft', 'Rejected', 'Cancelled')
    	)
		)""".format(user=user)

