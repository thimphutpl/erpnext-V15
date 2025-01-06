# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

'''
------------------------------------------------------------------------------------------------------------------------------------------
Version          Author         Ticket#           CreatedOn          ModifiedOn          Remarks
------------ --------------- --------------- ------------------ -------------------  -----------------------------------------------------
3.0               SHIV		                     28/01/2019                          Original Version
------------------------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import nowdate, cint, flt
# from erpnext.hr.doctype.approver_settings.approver_settings import get_final_approver
from hrms.hr.hr_custom_functions import get_officiating_employee
from frappe.utils.nestedset import get_ancestors_of

class CustomWorkflow:
	def __init__(self, doc):
		self.doc = doc
		self.new_state = self.doc.workflow_state
		self.old_state = self.doc.get_db_value("workflow_state")

		self.field_map 		= get_field_map()
		self.doc_approver	= self.field_map[self.doc.doctype]
		self.field_list		= ["user_id","employee_name","designation","name"]

		if self.doc.doctype != "Material Request" and self.doc.doctype not in ("Asset Issue Details", "Compile Budget","POL Expense","Vehicle Request", "Repair And Services", "Asset Movement", "Budget Reappropiation", "Employee Advance", "Prepare Audit Plan"):
			self.employee		= frappe.db.get_value("Employee", self.doc.employee, self.field_list)
			self.reports_to = frappe.db.get_value("Employee", {"name":frappe.db.get_value("Employee", self.doc.employee, "reports_to")}, self.field_list)
			
			if self.doc.doctype in ("Travel Request","Travel Authorization", "Travel Claim","Employee Separation","Overtime Application"):
				if frappe.db.get_value("Employee", self.doc.employee, "expense_approver"):
					self.expense_approver = frappe.db.get_value("Employee", {"user_id":frappe.db.get_value("Employee", self.doc.employee, "expense_approver")}, self.field_list)
				else:
					frappe.throw('Expense Approver not set for employee {}'.format(self.doc.employee))
			self.supervisors_supervisor = frappe.db.get_value("Employee", frappe.db.get_value("Employee", frappe.db.get_value("Employee", self.doc.employee, "reports_to"), "reports_to"), self.field_list)
			self.hr_approver	= frappe.db.get_value("Employee", frappe.db.get_single_value("HR Settings", "hr_approver"), self.field_list)
			if not self.hr_approver:
				frappe.throw("Please set HR Approver in HR Settings")
			self.hrgm = frappe.db.get_value("Employee",frappe.db.get_single_value("HR Settings","hrgm"), self.field_list)
			self.ceo= frappe.db.get_value("Employee", frappe.db.get_value("Employee", {"designation": "Chief Executive Officer", "status": "Active"},"name"), self.field_list)
			self.pms_appealer  = frappe.db.get_value("Employee", frappe.db.get_single_value("PMS Setting", "approver"), self.field_list)
			# self.dept_approver	= frappe.db.get_value("Employee", frappe.db.get_value("Department", str(frappe.db.get_value("Employee", self.doc.employee, "department")), "approver"), self.field_list)
			self.gm_approver	= frappe.db.get_value("Employee", frappe.db.get_value("Department",{"department_name":str(frappe.db.get_value("Employee", self.doc.employee, "division"))}, "approver_hod"),self.field_list)
			self.general_manager = frappe.db.get_value("Employee", frappe.db.get_value("Department",str(frappe.db.get_value("Employee",self.doc.employee,"division")),"approver_hod"),self.field_list)

			if self.doc.doctype in ["Leave Encashment","POL","Leave Application","Vehicle Request"]:
				self.adm_section_manager = frappe.db.get_value("Employee",{"user_id":frappe.db.get_value(
					"Department Approver",
					{"parent": "Administration Section - SMCL", "parentfield": "expense_approvers", "idx": 1},
					"approver",
				)},self.field_list)
		if self.doc.doctype == "Asset Movement":
			department = frappe.db.get_value("Employee",self.doc.from_employee, "department")
			if not department:
				frappe.throw("Department not set for {}".format(self.doc.from_employee))
			if department != "CHIEF EXECUTIVE OFFICE - SMCL":
				self.asset_verifier = frappe.db.get_value("Employee",{"user_id":frappe.db.get_value(
						"Department Approver",
						{"parent": department, "parentfield": "expense_approvers", "idx": 1},
						"approver",
					)},self.field_list)
				if not self.asset_verifier:
					self.asset_verifier = frappe.get_value("Department", department, "approver")
			else:
				self.asset_verifier = frappe.db.get_value("Employee", frappe.db.get_value("Employee", {"designation": "Chief Executive Officer", "status": "Active"},"name"), self.field_list)
		
		if self.doc.doctype in ("POL Expense"):
			department = frappe.db.get_value("Employee", {"user_id":self.doc.owner},"department")
			section = frappe.db.get_value("Employee", {"user_id":self.doc.owner},"section")
			if section in ("Chunaikhola Dolomite Mines - SMCL","Samdrup Jongkhar - SMCL"):
				self.pol_approver = frappe.db.get_value("Employee",{"user_id":frappe.db.get_value(
					"Department Approver",
					{"parent": section, "parentfield": "expense_approvers", "idx": 1},
					"approver",
				)},self.field_list)
			else:
				self.pol_approver = frappe.db.get_value("Employee",{"user_id":frappe.db.get_value(
					"Department Approver",
					{"parent": department, "parentfield": "expense_approvers", "idx": 1},
					"approver",
				)},self.field_list)
		if self.doc.doctype in ("Budget Reappropiation"):
			department = frappe.db.get_value("Employee", {"user_id":self.doc.owner},"department")
			section = frappe.db.get_value("Employee", {"user_id":self.doc.owner},"section")
			self.ceo= frappe.db.get_value("Employee", frappe.db.get_value("Employee", {"designation": "Chief Executive Officer", "status": "Active"},"name"), self.field_list)
			if section in ("Chunaikhola Dolomite Mines - SMCL","Samdrup Jongkhar - SMCL"):
				self.budget_reappropiation_approver = frappe.db.get_value("Employee",{"user_id":frappe.db.get_value(
					"Department Approver",
					{"parent": section, "parentfield": "expense_approvers", "idx": 1},
					"approver",
				)},self.field_list)
			else:
				self.budget_reappropiation_approver = frappe.db.get_value("Employee",{"user_id":frappe.db.get_value(
					"Department Approver",
					{"parent": department, "parentfield": "expense_approvers", "idx": 1},
					"approver",
				)},self.field_list)
			if not self.budget_reappropiation_approver:
				frappe.throw("No employee found for user id(expense approver) {}".format(frappe.db.get_value(
					"Department Approver",
					{"parent": department, "parentfield": "expense_approvers", "idx": 1},
					"approver",
				)))
		if self.doc.doctype == "Employee Advance":
			if self.doc.advance_type != "Imprest Advance":
				self.hr_approver	= frappe.db.get_value("Employee", frappe.db.get_single_value("HR Settings", "hr_approver"), self.field_list)
				if self.doc.employee == self.hr_approver[3]:
					self.hr_approver = frappe.db.get_value("Employee", frappe.db.get_single_value("HR Settings", "hrgm"), self.field_list)
			else:
				self.imprest_verifier = frappe.db.get_value("Employee",{'user_id':frappe.db.get_value("Employee",self.doc.employee,"expense_approver")},self.field_list)
				department = frappe.db.get_value("Employee", self.doc.employee ,"department")
				if not department:
					frappe.throw("Set department for {}".format(self.doc.employee))
					
				if not self.imprest_verifier:
					frappe.throw("Please Set Expense Approver for the Department <b>{}</b>".format(department))

				employee_section = frappe.db.get_value("Employee", self.doc.employee, "section")
				employee_branch = frappe.db.get_value("Employee", self.doc.employee, "branch")
				if employee_section and employee_section in ("Chunaikhola Dolomite Mines - SMCL", "Samdrup Jongkhar - SMCL"):
					self.imprest_approver = frappe.db.get_value("Employee", {"name":frappe.db.get_value("Department", employee_section ,"approver")}, self.field_list)

				elif employee_branch in ("Chunaikhola Dolomite Mine", "Regional Sales and Logistic Office Samdrup Jongkhar") and employee_section not in ("Chunaikhola Dolomite Mines - SMCL", "Samdrup Jongkhar - SMCL"):
					if employee_branch == "Chunaikhola Dolomite Mine":
						self.imprest_approver = frappe.db.get_value("Employee", {"name":frappe.db.get_value("Department", "Chunaikhola Dolomite Mines - SMCL" ,"approver")}, self.field_list)
					else:
						self.imprest_approver = frappe.db.get_value("Employee", {"name":frappe.db.get_value("Department", "Samdrup Jongkhar - SMCL" ,"approver")}, self.field_list)
				else:
					self.imprest_approver = frappe.db.get_value("Employee", {"name":frappe.db.get_value("Department", department ,"approver")}, self.field_list)
					if not self.imprest_verifier:
						frappe.throw("Set expense approver for SALES & LOGISTICS DEPARTMENT - SMCL department")

		if self.doc.doctype == "Material Request":
			# self.expense_approver = frappe.db.get_value("Employee", {"user_id":frappe.db.get_value("Employee", {"user_id":self.doc.owner}, "expense_approver")}, self.field_list)
			self.employee = frappe.db.get_value("Employee", {"user_id":self.doc.owner}, self.field_list)
			self.branch_approver = frappe.db.get_value("Employee",{'user_id': frappe.db.get_value("Approver Item", {"cost_center": self.doc.cost_center}, "approver")},self.field_list)
			# if self.doc.material_request_type == "Material Issue":
			# 	self.warehouse_manager = frappe.db.get_value("Employee",{'user_id':frappe.db.get_value("Warehouse",self.doc.set_warehouse,"email_id")},self.field_list)
			# elif self.doc.material_request_type == "Material Transfer":
			# 	self.warehouse_manager = frappe.db.get_value("Employee",{'user_id':frappe.db.get_value("Warehouse",self.doc.set_from_warehouse,"email_id")},self.field_list)
			
			self.reports_to	= frappe.db.get_value("Employee", frappe.db.get_value("Employee", {'user_id':self.doc.owner}, "reports_to"), self.field_list)
			# self.general_manager = frappe.db.get_value("Employee", frappe.db.get_value("Department",{"department_name":str(frappe.db.get_value("Employee",{"user_id":self.doc.owner},"division")).split(" - ")[0]},"approver"),self.field_list)
		
		if self.doc.doctype == "Employee Benefits":
			self.hrgm = frappe.db.get_value("Employee",frappe.db.get_single_value("HR Settings","hrgm"), self.field_list)	

		if self.doc.doctype == "Repair And Services":
			self.expense_approver = frappe.db.get_value("Employee", {"user_id":frappe.db.get_value("Employee", {"user_id":self.doc.owner}, "expense_approver")}, self.field_list)
			self.hrgm = frappe.db.get_value("Employee",frappe.db.get_single_value("HR Settings","hrgm"), self.field_list)
		
		if self.doc.doctype == "Vehicle Request":
			department =frappe.db.get_value("Employee",self.doc.employee,"department")
			if not department:
				frappe.throw("set department for employee in employee master")
			if frappe.db.get_value("Employee", self.doc.employee, "expense_approver"):
				self.expense_approver		= frappe.db.get_value("Employee", {"user_id":frappe.db.get_value("Employee", self.doc.employee, "expense_approver")}, self.field_list)
			else:
				frappe.throw('Expense Approver not set for employee {}'.format(self.doc.employee))
			self.vehicle_mto = frappe.db.get_value("Employee",{"user_id":frappe.db.get_value("Department",department,"approver_id")},self.field_list)

		self.login_user		= frappe.db.get_value("Employee", {"user_id": frappe.session.user}, self.field_list)

		if not self.login_user and frappe.session.user != "Administrator":
			if "PERC Member" in frappe.get_roles(frappe.session.user):
				return
			frappe.throw("{0} is not added as the employee".format(frappe.session.user))

	def update_employment_status(self):
		emp_status = frappe.db.get_value("Leave Type", self.doc.leave_type, ["check_employment_status","employment_status"])
		if cint(emp_status[0]) and emp_status[1]:
			emp = frappe.get_doc("Employee", self.doc.employee)
			emp.employment_status = emp_status[1]
			emp.save(ignore_permissions=True)

	def notify_hr(self):
		receipients = []
		email_group = frappe.db.get_single_value("HR Settings","email_group")
		if not email_group:
			frappe.throw("HR Users Email Group not set in HR Settings.")
		hr_users = frappe.get_list("Email Group Member", filters={"email_group":email_group}, fields=['email'])
		if hr_users:
			receipients = [a['email'] for a in hr_users]
			parent_doc = frappe.get_doc(self.doc.doctype, self.doc.name)
			args = parent_doc.as_dict()
			if self.doc.doctype == "Leave Application":
				template = frappe.db.get_single_value('HR Settings', 'leave_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Leave Approval Notification in HR Settings."))
					return
			else:
				template = ""
			if not template:
				frappe.msgprint(_("Please set default template for {}.").format(self.doc.doctype))
				return
			email_template = frappe.get_doc("Email Template", template)
			message = frappe.render_template(email_template.response, args)

			self.notify({
				# for post in messages
				"message": message,
				"message_to": receipients,
				# for email
				"subject": email_template.subject
			})

	def set_approver(self, approver_type):
		if approver_type == "Supervisor":
			if self.doc.doctype in ("Travel Request","Employee Separation","Vehicle Request", "Material Request", "Repair And Services","Overtime Application"):
				officiating = get_officiating_employee(self.expense_approver[3])
				if officiating:
					officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
				vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.expense_approver[0]
				vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.expense_approver[1]
				if self.doc.doctype != "Vehicle Request":
					vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.expense_approver[2]
			else:
				officiating = get_officiating_employee(self.reports_to[3])
				if officiating:
					officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
				vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.reports_to[0]
				vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.reports_to[1]
				vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.reports_to[2]

		elif approver_type =="POL Approver":
			officiating = get_officiating_employee(self.pol_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.pol_approver[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.pol_approver[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.pol_approver[2]

		elif approver_type =="Asset Verifier":
			officiating = get_officiating_employee(self.asset_verifier[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.asset_verifier[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.asset_verifier[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.asset_verifier[2]
			
		elif approver_type =="Imprest Verifier":
			officiating = get_officiating_employee(self.imprest_verifier[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.imprest_verifier[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.imprest_verifier[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.imprest_verifier[2]

		elif approver_type =="Imprest Approver":
			officiating = get_officiating_employee(self.imprest_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.imprest_approver[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.imprest_approver[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.imprest_approver[2]

		elif approver_type == "Supervisors Supervisor":
			officiating = get_officiating_employee(self.supervisors_supervisor[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.supervisors_supervisor[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.supervisors_supervisor[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.supervisors_supervisor[2]
		
		elif approver_type == "Fleet Manager":
			officiating = get_officiating_employee(self.fleet_mto[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.fleet_mto[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.fleet_mto[1]
			# vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.fleet_mto[2]
		
		elif approver_type == "Fleet MTO":
			officiating = get_officiating_employee(self.vehicle_mto[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.vehicle_mto[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.vehicle_mto[1]
			# vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.vehicle_mto[2]

		elif approver_type == "Project Manager":
			if self.project_manager == None:
				frappe.throw("""No Project Manager set in Project Definition <a href="#Form/Project%20Definition/{0}">{0}</a>""".format(frappe.db.get_value("Project",self.doc.reference_name,"project_definition")))
			officiating = get_officiating_employee(self.project_manager[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.project_manager[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.project_manager[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.project_manager[2]
		
		elif approver_type == "HR":
			officiating = get_officiating_employee(self.hr_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.hr_approver[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.hr_approver[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.hr_approver[2]
		
		elif approver_type == "HRGM":
			officiating = get_officiating_employee(self.hrgm[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.hrgm[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.hrgm[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.hrgm[2]

		elif approver_type == "Warehouse Manager":
			officiating = get_officiating_employee(self.warehouse_manager[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.warehouse_manager[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.warehouse_manager[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.warehouse_manager[2]
		
		elif approver_type == "Branch Approver":
			officiating = get_officiating_employee(self.branch_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.branch_approver[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.branch_approver[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.branch_approver[2]

		elif approver_type == "Manager Power":
			officiating = get_officiating_employee(self.power_section_manager[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.power_section_manager[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.power_section_manager[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.power_section_manager[2]

		elif approver_type == "ADM":
			officiating = get_officiating_employee(self.adm_section_manager[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.adm_section_manager[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.adm_section_manager[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.adm_section_manager[2]
		
		elif approver_type == "General Manager":
			# frappe.throw(str(self.general_manager))
			officiating = get_officiating_employee(self.general_manager[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.general_manager[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.general_manager[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.general_manager[2]
		
		elif approver_type == "GMM":
			officiating = get_officiating_employee(self.gm_marketing[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.gm_marketing[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.gm_marketing[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.gm_marketing[2]
		
		elif approver_type == "GMO":
			officiating = get_officiating_employee(self.gmo[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.gmo[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.gmo[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.gmo[2]
		
		elif approver_type == "Regional Director":
			officiating = get_officiating_employee(self.regional_director[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.regional_director[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.regional_director[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.regional_director[2]
		
		elif approver_type == "Department Head":
			officiating = get_officiating_employee(self.dept_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.dept_approver[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.dept_approver[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.dept_approver[2]
		
		elif approver_type == "GM":
			# frappe.msgprint(str(self.gm_approver))
			officiating = get_officiating_employee(self.gm_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.gm_approver[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.gm_approver[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.gm_approver[2]
		
		elif approver_type == "CEO":
			officiating = get_officiating_employee(self.ceo[3])
			# frappe.throw(str(officiating))
			if officiating: 
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.ceo[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.ceo[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.ceo[2]
		
		elif approver_type == "GM":
			#frappe.throw(str(officiating))
			officiating = get_officiating_employee(self.reports_to[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.reports_to[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.reports_to[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.reports_to[2]
		
		elif approver_type == "PMS Appealer":
			officiating = get_officiating_employee(self.reports_to[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.pms_appealer[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.pms_appealer[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.pms_appealer[2]
		
		elif approver_type == "Budget Reappropiation":
			officiating = get_officiating_employee(self.budget_reappropiation_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.budget_reappropiation_approver[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.budget_reappropiation_approver[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.budget_reappropiation_approver[2]
		else:
			frappe.throw(_("Invalid approver type for Workflow"))


	def apply_workflow(self):
		if (self.doc.doctype not in self.field_map) or not frappe.db.exists("Workflow", {"document_type": self.doc.doctype, "is_active": 1}):
			return

		if self.doc.doctype == "Leave Application":
			self.leave_application()	
		elif self.doc.doctype == "Leave Encashment":
			self.leave_encashment()
		elif self.doc.doctype == "Salary Advance":
			self.salary_advance()
		elif self.doc.doctype == "Travel Request":
			self.travel_request()
		elif self.doc.doctype in ("Travel Authorization", "Travel Adjustment"):
			self.travel_authorization()
		elif self.doc.doctype == "Travel Claim":
			self.travel_claim()		
		elif self.doc.doctype == "Vehicle Request":
			self.vehicle_request()
		elif self.doc.doctype == "Repair And Services":
			self.repair_services()
		elif self.doc.doctype == "Overtime Application":
			self.overtime_application()
		elif self.doc.doctype == "Material Request":
			self.material_request()		
		elif self.doc.doctype == "Employee Advance":
			self.employee_advance()
		elif self.doc.doctype == "Employee Transfer":
			self.employee_transfer()
		elif self.doc.doctype == "Employee Benefit Claim":
			self.employee_benefit_claim()
		elif self.doc.doctype == "POL Expense":
			self.pol_expenses()
		elif self.doc.doctype == "Budget Reappropiation":
			self.budget_reappropiation()
		elif self.doc.doctype == "Employee Separation":
			self.employee_separation()
		elif self.doc.doctype == "Employee Benefits":
			self.employee_benefits()
		elif self.doc.doctype == "Coal Raising Payment":
			self.coal_raising_payment()
		elif self.doc.doctype == "POL":
			self.pol()
		elif self.doc.doctype in ("Asset Issue Details","Project Capitalization"):
			self.asset()
		elif self.doc.doctype == "Compile Budget":
			self.compile_budget()
		elif self.doc.doctype == "Asset Movement":
			self.asset_movement()
		elif self.doc.doctype == "Target Set Up":
			self.target_set_up_and_review()
		elif self.doc.doctype == "Review":
			self.target_set_up_and_review()
		elif self.doc.doctype == "Performance Evaluation":
			self.performance_evaluation()
		elif self.doc.doctype == "SWS Application":
			self.sws_application()
		elif self.doc.doctype == "Prepare Audit Plan":
			self.prepare_audit_plan()
		elif self.doc.doctype == "SWS Membership":
			self.sws_membership()
		elif self.doc.doctype == "Contract Renewal Application":
			self.contract_renewal_application()
		elif self.doc.doctype == "Promotion Application":
			self.promotion_application()
		elif self.doc.doctype == "PMS Appeal":
			self.pms_appeal()
		else:
			frappe.throw(_("Workflow not defined for {}").format(self.doc.doctype))
	
	def compile_budget(self):
		if not self.old_state:
			return
		elif self.old_state.lower() == "Draft".lower() and self.new_state.lower() != "Draft".lower():
			if self.new_state.lower() == "Waiting RD Approval".lower() or self.new_state.lower() == "Waiting GM Approval".lower():
				if self.doc.budget_level == "Region":
					approver = frappe.db.get_value("Employee", frappe.db.sql("select approver from tabDepartment where name like '%{}%' and is_region=1".format(self.doc.region))[0][0], self.field_list)
				elif self.doc.budget_level == "Division":
					approver = frappe.db.get_value("Employee", frappe.db.get_value("Department", self.doc.division, "approver"), self.field_list)
				officiating = get_officiating_employee(approver[3])
				if officiating:
					officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
				vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else approver[0]
				vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else approver[1]
			else:
				pass
		elif self.old_state.lower() in ("Waiting RD Approval".lower(), "Rejected by GMO".lower()) and self.new_state.lower() == "Waiting GMO Approval".lower():
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only <b>{}</b> can Forward/Reject".format(self.doc.approver_name))
			self.doc.old_approver_id = self.doc.approver
			self.doc.old_approver = self.doc.approver_name
			self.doc.rejected_remarks = ""

			approver = frappe.db.get_value("Employee", frappe.db.get_value("Department", "Operations Division - BTL", "approver"), self.field_list)
			officiating = get_officiating_employee(approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else approver[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else approver[1]
		elif self.old_state.lower() in ("Waiting GM Approval".lower(),"Waiting RD Approval".lower()) and self.new_state.lower() in ("Rejected by GM".lower(), "Rejected by RD".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only <b>{}</b> can Forward/Reject".format(self.doc.approver_name))
		elif self.old_state.lower() == "Waiting GMO Approval".lower() and self.new_state.lower() == "Rejected by GMO".lower():
			self.doc.old_approver_id = ""
			self.doc.old_approver = ""
			approver = frappe.db.get_value("Employee", frappe.db.sql("select approver from tabDepartment where name like '%{}%' and is_region=1".format(self.doc.region))[0][0], self.field_list)
			officiating = get_officiating_employee(approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else approver[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else approver[1]
		elif self.new_state.lower() == "Waiting Finance Department Approval".lower():
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only <b>{}</b> can Forward/Reject".format(self.doc.approver_name))
		elif self.old_state.lower() in ("Rejected by GM".lower(), "Rejected by RD".lower(), "Rejected by Finance Department".lower(), "Rejected by Management".lower(), "Rejected by Board".lower()):
			self.doc.rejected_remarks = ""
	
	def promotion_application(self):
		if self.new_state.lower() == ("Waiting Supervisor Approval".lower()):
			self.set_approver("Supervisor")
		elif self.new_state.lower() == ("Waiting Hr Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Forward this Application".format(self.doc.approver_name))
			self.set_approver("HR")
		elif self.new_state.lower() == ("Approved".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Approve this Application".format(self.doc.approver_name))

		elif self.new_state.lower() == ("Rejected".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Reject this Application".format(self.doc.approver_name))
		else:
			frappe.throw(_("Invalid Workflow State {}").format(self.doc.workflow_state))
	
	def prepare_audit_plan(self):
		if self.new_state.lower() == ("Waiting Approval".lower()):
			vars(self.doc)[self.doc_approver[0]] = self.doc.supervisor_email
			vars(self.doc)[self.doc_approver[1]] = self.doc.supervisor_name
			vars(self.doc)[self.doc_approver[2]] = self.doc.supervisor_designation
			# frappe.throw(str(self.doc.approver))
		elif self.new_state.lower() == ("Approved".lower()):
			# frappe.throw(str(self.doc.approver))
			if self.doc.supervisor_email != frappe.session.user:
				frappe.throw("Only {} can Approve this Application".format(self.doc.supervisor_email))

		
	
	def target_set_up_and_review(self):
		if self.new_state.lower() in ("Draft".lower()):
			if frappe.session.user != self.doc.owner:
				frappe.throw("Only {} can apply this leave".format(self.doc.owner))

		elif self.new_state.lower() == ("Waiting Supervisor Approval".lower()):
			self.set_approver("Supervisor")

		elif self.new_state.lower() == ("Approved".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Approve this Application".format(self.doc.approver_name))

		elif self.new_state.lower() == ("Rejected".lower()):
			employee_user = frappe.db.get_value("Employee", self.employee, "user_id")
			if frappe.session.user not in (self.doc_approver, self.doc_owner, employee_user):
				frappe.throw("Only {}, {}, {} can Reject this Application".format(self.doc_approver, self.doc_owner, employee_user))
		else:
			frappe.throw(_("Invalid Workflow State {}").format(self.doc.workflow_state))

	def performance_evaluation(self):
		if self.new_state.lower() in ("Draft".lower()):
			if frappe.session.user != self.doc.owner:
				frappe.throw("Only {} can apply this leave".format(self.doc.owner))

		elif self.new_state.lower() == ("Waiting Supervisor Approval".lower()):
			self.set_approver("Supervisor")

		elif self.new_state.lower() == ("Waiting Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Forward this Application".format(self.doc.approver_name))
			self.set_approver("Supervisors Supervisor")
		elif self.new_state.lower() == ("Approved".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Approve this Application".format(self.doc.approver_name))

		elif self.new_state.lower() == ("Rejected".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Reject this Application".format(self.doc.approver_name))
		else:
			frappe.throw(_("Invalid Workflow State {}").format(self.doc.workflow_state))

	def pms_appeal(self):
		if self.new_state.lower() == ("Waiting Approval".lower()):
			self.set_approver("PMS Appealer")

		elif self.new_state.lower() == ("Approved".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Approve this Application".format(self.doc.approver_name))

		elif self.new_state.lower() == ("Rejected".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Reject this Application".format(self.doc.approver_name))
		else:
			frappe.throw(_("Invalid Workflow State {}").format(self.doc.workflow_state))
	
	def contract_renewal_application(self):
	
		if self.new_state.lower() == ("Waiting Supervisor Approval".lower()):
			self.set_approver("Supervisor")
		elif self.new_state.lower() == ("Waiting Hr Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Forward this Application".format(self.doc.approver_name))
			self.set_approver("HR")
		elif self.new_state.lower() == ("Approved".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Approve this Application".format(self.doc.approver_name))

		elif self.new_state.lower() == ("Rejected".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Reject this Application".format(self.doc.approver_name))
		else:
			frappe.throw(_("Invalid Workflow State {}").format(self.doc.workflow_state))
	



	def pol_expenses(self):
		if self.new_state and self.old_state and self.new_state.lower() == self.old_state.lower():
			return
		if self.new_state.lower() in ("Waiting GM Approval".lower()):
			if self.doc.owner != frappe.session.user:
				frappe.throw("Only {} can Apply this Document".format(self.doc.owner))
			self.set_approver("POL Approver")
		if self.new_state.lower() in ("Approved".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Approve this Document".format(self.doc.approver))
		if self.new_state.lower() in ("Rejected".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can reject this Document".format(self.doc.approver))

	def employee_separation(self):
		if self.new_state.lower() in ("Waiting Supervisor Approval".lower()):
			self.set_approver("Supervisor")
		
		elif self.new_state.lower() in ("Waiting GM Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Forward this document".format(self.doc.approver))
			self.set_approver("General Manager")
		
		elif self.new_state.lower() in ("Waiting CEO Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Forward this document".format(self.doc.approver))
			self.set_approver("CEO")

		elif self.new_state.lower() in ("Approved".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit/submit this document".format(self.doc.approver))

	def employee_benefits(self):
		if self.new_state.lower() in ("Waiting HR Approval".lower()):
			self.set_approver("HR")
		if self.new_state.lower() in ("Waiting GM Approval".lower()):
			# if self.new_state.lower() == "Waiting GM Approval".lower():
			# 	if "HR User" not in frappe.get_roles(frappe.session.user):
			# 		frappe.throw("Only HR can Apply this Appeal")
			if self.hr_approver[0] != frappe.session.user:
				frappe.throw("Only {} can edit/approve this documents".format(self.hr_approver[0]))
			self.set_approver("HRGM")

		elif self.new_state.lower() in ("Approved".lower()):
			if self.hrgm[0] != frappe.session.user:
				frappe.throw("Only {} can edit/submit this document".format(self.hrgm[0]))
					
	def coal_raising_payment(self):
		if self.new_state.lower() in ("Draft".lower(), "Waiting Supervisor Approval".lower()):
			if self.new_state.lower() == "Waiting Supervisor Approval".lower() and self.doc.owner != frappe.session.user:
				if "Production User" not in frappe.get_roles(frappe.session.user):
					frappe.throw("Only {} can Apply this Appeal".format(self.doc.employee_name))
			self.set_approver("Production Manager")
		elif self.new_state.lower() in ("Submitted".lower()):
			if "Production User" not in frappe.get_roles(frappe.session.user):
				if self.doc.approver != frappe.session.user:
					frappe.throw("Only {} can edit/submit this documents".format(self.doc.approver))
	def pol(self):
		if self.new_state.lower() in ("Waiting Supervisor Approval".lower()):
			self.set_approver("Supervisor")
		elif self.new_state.lower() in ("Waiting Approval".lower()):
			if self.doc.approver and self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can approve this document".format(self.doc.approver))
			if self.doc.region and self.doc.region != "Corporate Head Quarter":
				self.set_approver("Regional Director")
			else:
				if self.doc.equipment_category == "POWER EQUIPMENT":
					self.set_approver("Manager Power")
				else:
					if self.doc.branch == "Marketing Division, CHQ":
						self.set_approver("GMM")
					else:
						self.set_approver("ADM")
		elif self.new_state.lower() in ("Approved".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit/approve this documents".format(self.doc.approver))
		elif self.new_state.lower() in ("Cancelled".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can cancel this documents".format(self.doc.approver))

	def asset(self):
		if self.new_state.lower() in ("Waiting Verification".lower()):
			if frappe.session.user != self.doc.owner:
				if self.doc.doctype == "Project Capitalization" and "Projects Manager" not in frappe.get_roles(frappe.session.user):
					frappe.throw("Only {} can forward this Asset for verification.".format(self.doc.owner))
				if self.doc.doctype == "Asset Issue Details" and "Stock User" not in frappe.get_roles(frappe.session.user):
					frappe.throw("Only {} can forward this Asset for verification.".format(self.doc.owner))
		if self.new_state.lower() in ("Verified".lower()):
			if "Accounts User" not in frappe.get_roles(frappe.session.user) and "Projects Manager" not in frappe.get_roles(frappe.session.user):
				if self.old_state.lower() != self.new_state.lower():
					frappe.throw("Only Accounts User can verify for this Asset.")
		if self.new_state.lower() in ("Submitted".lower()):
			if frappe.session.user != self.doc.owner:
				frappe.throw("Only {} can submit this Asset".format(self.doc.owner))
		if self.new_state.lower() in ("Rejected".lower()):
			if "Accounts User" not in frappe.get_roles(frappe.session.user):
				frappe.throw("Only Accounts User can reject this Asset.")

	def leave_application(self):
		''' Leave Application Workflow
			1. Casual Leave, Earned Leave & Paternity Leave: 
				* Employee -> Supervisor
			2. Medical Leave:
				* Employee -> Department Head (if the leave is within 5 days)
				* Employee -> CEO (more than 5 days)
			3. Bereavement & Maternity:
				* Employee -> Department Head
			4. Extraordinary Leave:
				* Employee -> CEO 
		'''
		if self.new_state.lower() in ("Draft".lower()):
			if frappe.session.user != self.doc.owner:
				frappe.throw("Only {} can apply this leave".format(self.doc.owner))

		elif self.new_state.lower() == ("Waiting Approval".lower()):
			self.set_approver("Supervisor")

		elif self.new_state.lower() == ("Approved".lower()):
			if self.doc.supervisor != frappe.session.user:
				frappe.throw("Only {} can Approve this Leave Application".format(self.doc.supervisor))

		elif self.new_state.lower() == ("Rejected".lower()):
			if self.doc.supervisor != frappe.session.user:
				frappe.throw("Only {} can Reject this Leave Application".format(self.doc.supervisor))
		else:
			frappe.throw(_("Invalid Workflow State {}").format(self.doc.workflow_state))


	def leave_encashment(self):
		''' Leave Encashment Workflow
			1. Employee -> HR
		'''
		if self.new_state.lower() == "Waiting Approval".lower():
			self.set_approver("HR")
		elif self.new_state.lower() == "Approved".lower():
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Approve this Encashment".format(self.doc.approver_name))
		elif self.new_state.lower() in ('Rejected'):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Reject this Encashment".format(self.doc.approver_name))

	def sws_application(self):
		if self.new_state.lower() in ("Draft".lower(), "Waiting Supervisor Approval".lower()):
			self.set_approver("Supervisor")
			try:
				eid = frappe.db.get_value("Employee",self.doc.employee,"user_id")
			except:
				frappe.throw("User ID not set for Employee '{0}'".format(self.doc.employee))
	
		if self.new_state.lower() == "Waiting SWS User Approval".lower():
			if frappe.session.user != self.doc.supervisor:
						frappe.throw("Only {} can edit/approve this document".format(self.doc.supervisor))

		if self.new_state.lower() == "Waiting Accounts Approval".lower():
			self.doc.verified = 1
   
		if self.new_state.lower() =="Rejected".lower():
			self.doc.verified = 0
			self.doc.approval_status = "Rejected"
   
		if self.new_state.lower() =="Approved".lower():
			self.doc.approval_status = "Approved"
	
	def sws_membership(self):
		if self.new_state.lower() in ("Draft".lower(), "Waiting Supervisor Approval".lower()):
			self.set_approver("Supervisor")
		if self.new_state.lower() == "Waiting Hr Approval".lower() and self.old_state.lower() != "Waiting SWS User Approval".lower():
			if frappe.session.user != self.doc.supervisor:
				frappe.throw("Only {} can approver this document.".format(self.doc.supervisor))
			self.set_approver("HR")

	def salary_advance(self):
		''' Salary Advance Workflow
			1. Employee -> GM -> CEO -> HR
		'''	
		if self.new_state.lower() in ("Waiting CEO Approval".lower()):
			if "Director" not in frappe.get_roles(frappe.session.user) and "General Manager" not in frappe.get_roles(frappe.session.user):
				if self.doc.advance_approver != frappe.session.user:
					frappe.throw(_("Only {} can Verify this request").format(self.doc.advance_approver_name))	
			self.set_approver("CEO")
			self.doc.db_set("status",self.new_state)
		elif self.new_state.lower() in ("Waiting HR Approval".lower()):
			self.set_approver("HR")
			self.doc.db_set("status",self.new_state)
		elif self.new_state.lower() in ("Waiting GM Approval".lower()):
			self.set_approver("GM")
			self.doc.db_set("status",self.new_state)
		elif self.new_state.lower() == "Approved".lower():
			if self.doc.advance_approver != frappe.session.user:
				frappe.throw(_("Only {} can Approve this request").format(self.doc.advance_approver_name))	
			self.doc.db_set("status",self.new_state)	
		elif self.new_state.lower() == "Rejected":
			if self.doc.advance_approver != frappe.session.user:
				frappe.throw(_("Only {} can Reject this request").format(self.doc.advance_approver_name))
			self.doc.db_set("status",self.new_state)		
		elif self.new_state.lower() == "Cancelled".lower():
			if frappe.session.user not in (self.doc.advance_approver,"Administrator"):
				frappe.throw(_("Only {} can Cancel this document.").format(self.doc.advance_approver_name))
			self.doc.db_set("status",self.new_state)
	
	def travel_request(self):
		''' Travel Request Workflow
			1. Employee -> Supervisor -> HR Manager
		'''
		if self.new_state and self.old_state and self.new_state.lower() == self.old_state.lower():
			return

		if self.new_state.lower() in ("Waiting Approval".lower()):
			self.doc.check_advance_and_report()
			self.doc.check_date()
			self.set_approver("Supervisor")
			self.doc.document_status = "Draft"
		elif self.new_state == "Waiting Hr Approval":
			if self.doc.supervisor != frappe.session.user:
				frappe.throw("Only {} can Forware this request".format(self.doc.supervisor_name))
			self.set_approver("HR")	
		elif self.new_state.lower() == "Approved".lower():
			if self.doc.supervisor != frappe.session.user:
				frappe.throw("Only {} can Approve this request".format(self.doc.supervisor_name))
			self.doc.document_status = "Approved"
		elif self.new_state.lower() == 'Rejected'.lower():
			if self.doc.supervisor != frappe.session.user and self.new_state.lower() != self.old_state.lower():
				frappe.throw("Only {} can Reject this request".format(self.doc.supervisor_name))
			self.doc.document_status = "Rejected"
		elif self.new_state.lower() == "Cancelled".lower():
			if "HR User" not in frappe.get_roles(frappe.session.user):
				frappe.throw(_("Only {} can Cancel this Travel Request").format(self.doc.supervisor_name))
			self.doc.document_status = "Cancelled"

	def travel_authorization(self):
		if self.new_state.lower() in ("Waiting Supervisor Approval".lower()):
			if self.doc.owner != frappe.session.user and self.new_state.lower() != self.old_state.lower():
				frappe.throw("Only <b>{}</b> can Apply this request".format(self.doc.owner))
			self.set_approver("Supervisor")
			
		elif self.new_state.lower() == "Approved".lower():
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only <b>{}</b> can Approve this request".format(self.doc.approver_name))

		elif self.new_state.lower() in ("Rejected".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only the <b>{}</b> can Reject this request".format(self.doc.approver_name))

		elif self.new_state.lower() == "Cancelled".lower():
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only <b>{}</b> can Cancel this request".format(self.doc.approver_name))
	
	def travel_claim(self):
		if self.new_state.lower() in ("Waiting Supervisor Approval".lower()):
			if self.doc.owner != frappe.session.user and self.new_state.lower() != self.old_state.lower():
				frappe.throw("Only <b>{}</b> can Apply this request".format(self.doc.owner))
			self.set_approver("Supervisor")

		if self.new_state.lower() in ("Waiting HR Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only <b>{}</b> can Forward this request".format(self.doc.approver))
			# self.set_approver("HR")
			
		elif self.new_state.lower() == "Approved".lower():
			user_roles = frappe.get_roles(frappe.session.user)
			if "HR Manager" in user_roles:
				return
			else:
				frappe.throw("Only <b>{}</b> can Approve this request".format("HR Manager"))
			# if self.doc.approver != frappe.session.user:
			# 	frappe.throw("Only <b>{}</b> can Approve this request".format(self.doc.approver_name))

		elif self.new_state.lower() in ("Rejected".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only the <b>{}</b> can Reject this request".format(self.doc.approver_name))

		elif self.new_state.lower() == "Cancelled".lower():
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only <b>{}</b> can Cancel this request".format(self.doc.approver_name))

			
	def employee_advance(self):
		if self.new_state and self.old_state and self.new_state.lower() == self.old_state.lower():
			return
		if self.new_state.lower() in ("Waiting Hr Approval".lower()):
			if self.doc.owner != frappe.session.user:
				frappe.throw("Only {} can Apply this document".format(self.doc.owner))
			self.set_approver("HR")

		if self.new_state.lower() in ("Waiting Supervisor Approval".lower()):
			if self.doc.owner != frappe.session.user:
				frappe.throw("Only {} can Apply this document".format(self.doc.owner))
			self.set_approver("Imprest Verifier")

		if self.new_state.lower() in ("Waiting Approval".lower()):
			if self.doc.advance_approver_name != frappe.session.user:
				frappe.throw("Only {} can Forward this document".format(self.doc.advance_approver_name))
			self.set_approver("Imprest Approver")

		if self.new_state.lower() in ("Approved".lower()):
			if self.doc.advance_approver_name != frappe.session.user:
				frappe.throw("Only {} can Approve this document".format(self.doc.advance_approver_name))

	def vehicle_request(self):
		if self.new_state.lower() in ("Draft".lower()):
			if self.doc.owner != frappe.session.user:
				frappe.throw("Only {} can Apply this material request".format(self.doc.owner))
			self.set_approver("Supervisor")
		elif self.new_state.lower() in ("Waiting Supervisor Approval".lower()):
			if self.doc.owner != frappe.session.user and self.new_state != self.old_state:
				frappe.throw("Only {} can Apply this Vehicle Request".format(self.doc.owner))
			self.set_approver("Supervisor")
		elif self.new_state.lower() in ("Waiting MTO Approval".lower()):
			if self.doc.approver_id != frappe.session.user:
				frappe.throw("Only {} can forward this request".format(self.doc.approver_id))
			self.set_approver("Fleet MTO")
		elif self.new_state.lower() in ("Approved".lower()):
			if self.doc.approver_id != frappe.session.user:
				frappe.throw("Only {} can Approve this Vehicle Request".format(self.doc.approver_id))
	
	def asset_movement(self):
		if self.new_state and self.old_state and self.new_state.lower() == self.old_state.lower():
			return
		if self.new_state.lower() in ("Draft".lower()):
			if self.doc.owner != frappe.session.user:
				frappe.throw("Only the document owner can Apply this material request")
			self.set_approver("Asset Verifier")

		if self.new_state.lower() in ("Waiting for Verification".lower()):
			if self.doc.owner != frappe.session.user:
				frappe.throw("Only {} can Apply this request".format(self.doc.owner))
			self.set_approver("Asset Verifier")
			
	def budget_reappropiation(self):
		user_roles = frappe.get_roles(frappe.session.user)
		if self.new_state and self.old_state and self.new_state.lower() == self.old_state.lower():
			return
		if self.new_state.lower() in ("Draft".lower(),"Waiting for Verification".lower()):
			if self.doc.owner != frappe.session.user:
				frappe.throw("Only the document owner can Apply this document")

		if self.new_state.lower() in ("Waiting Approval".lower()):
			if "Budget Manager" not in user_roles:
				frappe.throw("Only Budget Manager Can verify this document")
			self.set_approver("Budget Reappropiation")

		if self.new_state.lower() in ("Waiting CEO Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can forward this document".format(self.doc.approver))
			self.set_approver("CEO")

		if self.new_state.lower() in ("Approved".lower()):
			if self.old_state.lower() in ("Waiting CEO Approval".lower()) and  "CEO" not in user_roles:
				frappe.throw("Only CEO can approve this document")
			elif self.doc.approver != frappe.session.user :
				frappe.throw("Only {} or CEO can approve this document".format(self.doc.approver))

		if self.new_state.lower() in ("Rejected".lower()):
			if "Budget Manager" in user_roles or "CEO" in user_roles or self.doc.approver == frappe.session.user:
				return
			else:
				frappe.throw("Only Budget Manager or {} Can reject this document".format(self.doc.approver))
	def repair_services(self):
		if self.new_state.lower() in ("Draft".lower()):
			cost_center = frappe.db.get_value("Employee",{"user_id":self.doc.owner},"cost_center")
			if cost_center == "CORPORATE HEAD OFFICE - SMCL":
				self.set_approver("ADM")
			else:
				self.set_approver("Supervisor")
		elif self.new_state.lower() in ("Waiting Supervisor Approval".lower()):
			if self.doc.owner != frappe.session.user and self.new_state != self.old_state:
				frappe.throw("Only {} can Apply".format(self.doc.owner))
		elif self.new_state.lower() in ("Waiting Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can forward this request".format(self.doc.approver))
			self.set_approver("HRGM")
		elif self.new_state.lower() in ("Approved".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Approve this document".format(self.doc.approver_id))

	def overtime_application(self):
		if self.new_state.lower() in ("Draft".lower(), "Waiting Supervisor Approval".lower()):
			self.set_approver("Supervisor")
		elif self.new_state.lower() == "Approved".lower():
			if self.doc.approver != frappe.session.user and "HR User" not in frappe.get_roles(frappe.session.user):
				frappe.throw("Only {} can Approve this request".format(self.doc.approver_name))
			self.doc.status = 'Approved'
		elif self.new_state.lower() in ('Rejected'.lower(), 'Rejected By Supervisor'.lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Reject this request".format(self.doc.approver_name))
		elif self.new_state.lower() == "Cancelled".lower():
			if "HR User" not in frappe.get_roles(frappe.session.user):
				if self.doc.approver != frappe.session.user:
					frappe.throw("Only {} can Cancel this request".format(self.doc.approver_name))

	def material_request(self):
		''' Material Request Workflow
			1. Employee -> MR Manager
		'''
		if self.new_state.lower() in ("Draft".lower()):
			if self.doc.owner != frappe.session.user:
				frappe.throw("Only the document owner can Apply this material request")

		# elif self.new_state.lower() in ("Waiting Supervisor Approval".lower()):
		# 	if self.doc.owner != frappe.session.user and self.new_state.lower()!= self.old_state.lower():
		# 		frappe.throw("Only the document owner can Apply this material request")
		# 	self.set_approver("Supervisor")
			
		elif self.new_state.lower() in ("Waiting Approval".lower()):
			if self.doc.owner != frappe.session.user and self.new_state.lower()!= self.old_state.lower():
				frappe.throw("Only the document owner can Apply this material request")
			self.set_approver("Branch Approver")

		# elif self.new_state.lower() in ("Waiting GM Approval".lower()):
		# 	if self.doc.approver != frappe.session.user:
		# 		frappe.throw("Only the {} can Approve this material request".format(self.doc.approver))
		# 	self.set_approver("General Manager")

		# elif self.new_state.lower() in ("Waiting CEO Approval".lower()):
		# 	if self.doc.approver != frappe.session.user:
		# 		frappe.throw("Only the {} can Approve this material request".format(self.doc.approver))
		# 	self.set_approver("MR CEO")

		elif self.new_state.lower() in ("Approved".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only the {} can Approve this material request".format(self.doc.approver))

		elif self.new_state.lower() in ("Rejected".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only the {} can Reject this material request".format(self.doc.approver))

	def employee_benefit_claim(self):
		workflow_state    = self.doc.get("workflow_state").lower()
		if workflow_state == "Draft".lower():
			# if doc.purpose == "Separation":
			if not "HR Manager" in frappe.get_roles(frappe.session.user):
				frappe.throw("Only HR user with role HR Manager can create the employee benefit with purpose Separation")

		elif workflow_state == "Waiting Approval".lower():
			# if doc.purpose == "Separation":
			self.set_approver("HR")
			if not "HR Manager" in frappe.get_roles(frappe.session.user):
				frappe.throw("Only HR user with role HR Manager can create the employee benefit with purpose Separation")

		elif workflow_state == "Approved".lower():
			if self.doc.docstatus == 0 and self.doc.workflow_state == "Approved":
				self.doc.workflow_state == "Waiting Approval"
			if not "Chief PCD" in frappe.get_roles(frappe.session.user):
				frappe.throw(_("Only Chief PCD can approve this application").format(title="Invalid Operation"))
			vars(self.doc)[self.doc_approver[0]] = self.login_user[0]
			vars(self.doc)[self.doc_approver[1]] = self.login_user[1]
	
		elif workflow_state == "Rejected".lower():
			if not "Chief PCD" in frappe.get_roles(frappe.session.user):
				if workflow_state != self.doc.get_db_value("workflow_state"):
					frappe.throw(_("Only Cheif PCD can reject this application").format(title="Invalid Operation"))
		else:
			pass

	def employee_transfer(self):
		
		if self.doc.workflow_state == "Rejected":
			if not self.doc.rejection_reason:
				frappe.throw("Please input a rejection reason")

		elif self.new_state.lower() == "Waiting Supervisor Approval".lower():
			self.set_approver("Supervisor")

			
		elif self.new_state.lower() == "Waiting GM Approval".lower():
			if self.expense_approver[0] != frappe.session.user:
				frappe.throw("Only {} can Forward this document.".format(self.expense_approver[0]))
			self.set_approver("General Manager")

		elif self.new_state.lower() == "Waiting Hr Approval".lower():
			# frappe.throw(str(self.hrgm))
			if self.general_manager[0] != frappe.session.user:
				frappe.throw("Only {} can Forward this document.".format(self.general_manager[0]))
			self.set_approver("HR")
   
		elif self.new_state.lower() =="Rejected".lower():
			if (self.hr_approver[0] != frappe.session.user) or (self.doc.supervisor != frappe.session.user):
				frappe.throw("Only {} or {} can reject this document.".format(self.doc.supervisor, self.hr_approver[0]))
   
		elif self.new_state.lower() =="Approved".lower():
			if self.hr_approver[0] != frappe.session.user:
				frappe.throw("Only {} can approve or edit this document.".format(self.hr_approver[0]))

	def notify(self, args):
		args = frappe._dict(args)
		# args -> message, message_to, subject

		contact = args.message_to
		if not isinstance(contact, list):
			if not args.notify == "employee":
				contact = frappe.get_doc('User', contact).email or contact

		sender      	    = dict()
		sender['email']     = frappe.get_doc('User', frappe.session.user).email
		sender['full_name'] = frappe.utils.get_fullname(sender['email'])

		try:
			frappe.sendmail(
				recipients = contact,
				sender = sender['email'],
				subject = args.subject,
				message = args.message,
			)
			frappe.msgprint(_("Email sent to {0}").format(contact))
		except frappe.OutgoingEmailError:
			pass

class NotifyCustomWorkflow:
	def __init__(self,doc):
		self.doc 			= doc
		self.old_state 		= self.doc.get_db_value("workflow_state")
		self.new_state 		= self.doc.workflow_state
		self.field_map 		= get_field_map()
		self.doc_approver	= self.field_map[self.doc.doctype]
		self.field_list		= ["user_id","employee_name","designation","name"]
		if self.doc.doctype not in ("Material Request","Asset Issue Details", "Project Capitalization", "POL Expense", "Prepare Audit Plan"):
			self.employee   = frappe.db.get_value("Employee", self.doc.employee, self.field_list)
		else:
			self.employee = frappe.db.get_value("Employee", {"user_id":self.doc.owner}, self.field_list)

	def notify_employee(self):
		if self.doc.doctype not in ("Material Request","Asset Issue Details","Repair And Services","Project Capitalization","POL Expense"):
			employee = frappe.get_doc("Employee", self.doc.employee)
		else:
			employee = frappe.get_doc("Employee", frappe.db.get_value("Employee",{"user_id":self.doc.owner},"name"))
		if not employee.user_id:
			return

		parent_doc = frappe.get_doc(self.doc.doctype, self.doc.name)
		args = parent_doc.as_dict()

		if self.doc.doctype == "Leave Application":
			template = frappe.db.get_single_value('HR Settings', 'leave_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Leave Status Notification in HR Settings."))
				return
		elif self.doc.doctype == "Leave Encashment":
			template = frappe.db.get_single_value('HR Settings', 'encashment_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Encashment Status Notification in HR Settings."))
				return
		elif self.doc.doctype == "Salary Advance":
			template = frappe.db.get_single_value('HR Settings', 'advance_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Advance Status Notification in HR Settings."))
				return
		elif self.doc.doctype == "Travel Request":
			template = frappe.db.get_single_value('HR Settings', 'authorization_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Authorization Status Notification in HR Settings."))
				return
		elif self.doc.doctype == "Overtime Application":
			template = frappe.db.get_single_value('HR Settings', 'overtime_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Overtime Status Notification in HR Settings."))
				return

		elif self.doc.doctype == "Employee Benefits":
			template = frappe.db.get_single_value('HR Settings', 'benefits_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Employee Benefits Status Notification in HR Settings."))
				return
		elif self.doc.doctype == "Employee Separation":
			template = frappe.db.get_single_value('HR Settings', 'employee_separation_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Employee Separation Status Notification in HR Settings."))
				return
		elif self.doc.doctype == "Employee Transfer":
			template = frappe.db.get_single_value('HR Settings', 'employee_transfer_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Employee Transfer Status Notification in HR Settings."))
				return
		elif self.doc.doctype == "POL Expense":
			template = frappe.db.get_single_value('Maintenance Settings', 'pol_expense_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for POL Expense Status Notification in Maintenance Settings."))
				return
		elif self.doc.doctype == "Material Request":
			template = frappe.db.get_single_value('Stock Settings', 'mr_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Material Request Status Notification in Stock Settings."))
				return

		elif self.doc.doctype == "Asset Issue Details":
			template = frappe.db.get_single_value('Asset Settings', 'asset_issue_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Asset Issue Status Notification in Asset Settings."))
				return
		elif self.doc.doctype == "Project Capitalization":
			template = frappe.db.get_single_value('Asset Settings', 'asset_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Asset Status Notification in Asset Settings."))
				return
		else:
			template = ""

		if not template:
			frappe.msgprint(_("Please set default template for {}.").format(self.doc.doctype))
			return
		email_template = frappe.get_doc("Email Template", template)
		message = frappe.render_template(email_template.response, args)
		if employee :
			self.notify({
				# for post in messages
				"message": message,
				"message_to": employee.user_id,
				# for email
				"subject": email_template.subject,
				"notify": "employee"
			})

	def notify_approver(self):
		if self.doc.get(self.doc_approver[0]):
			parent_doc = frappe.get_doc(self.doc.doctype, self.doc.name)
			args = parent_doc.as_dict()
			if self.doc.doctype == "Leave Application":
				template = frappe.db.get_single_value('HR Settings', 'leave_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Leave Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Leave Encashment":
				template = frappe.db.get_single_value('HR Settings', 'encashment_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Encashment Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Salary Advance":
				template = frappe.db.get_single_value('HR Settings', 'advance_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Advance Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Travel Request":
				template = frappe.db.get_single_value('HR Settings', 'authorization_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Authorization Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Overtime Application":
				template = frappe.db.get_single_value('HR Settings', 'overtime_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Overtime Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Employee Transfer":
				template = frappe.db.get_single_value('HR Settings', 'employee_transfer_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Employee Transfer Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Employee Benefits":
				template = frappe.db.get_single_value('HR Settings', 'benefits_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Employee Benefits Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Employee Separation":
				template = frappe.db.get_single_value('HR Settings', 'employee_separation_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Employee Separation Approval Notification in HR Settings."))
					return 
			elif self.doc.doctype == "POL Expense":
				template = frappe.db.get_single_value('Maintenance Settings', 'pol_expense_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for POL Expense Approval Notification in Maintenance Settings."))
					return
			elif self.doc.doctype == "Repair And Services":
				template = frappe.db.get_single_value('Maintenance Settings', 'repair_and_services_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Repair And Services Approval Notification in Maintenance Settings."))
					return
			elif self.doc.doctype == "POL":
				template = frappe.db.get_single_value('Maintenance Settings', 'pol_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for POL Approval Notification in Maintenance Settings."))
					return
			elif self.doc.doctype == "Material Request":
				template = frappe.db.get_single_value('Stock Settings', 'mr_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Material Request Approval Notification in Stock Settings."))
					return

			elif self.doc.doctype == "Asset Issue Details":
				template = frappe.db.get_single_value('Asset Settings', 'asset_issue_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Asset Issue Approval Notification in Asset Settings."))
					return
	
			elif self.doc.doctype == "Project Capitalization":
				template = frappe.db.get_single_value('Asset Settings', 'asset_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Asset Approval Notification in Asset Settings."))
					return
			else:
				template = ""

			if not template:
				frappe.msgprint(_("Please set default template for {}.").format(self.doc.doctype))
				return
			email_template = frappe.get_doc("Email Template", template)
			message = frappe.render_template(email_template.response, args)
			self.notify({
				# for post in messages
				"message": message,
				"message_to": self.doc.get(self.doc_approver[0]),
				# for email
				"subject": email_template.subject
			})
			

	def notify_hr_users(self):
		receipients = []
		email_group = frappe.db.get_single_value("HR Settings","email_group")
		if not email_group:
			frappe.throw("HR Users Email Group not set in HR Settings.")
		hr_users = frappe.get_list("Email Group Member", filters={"email_group":email_group}, fields=['email'])
		if hr_users:
			receipients = [a['email'] for a in hr_users]
			parent_doc = frappe.get_doc(self.doc.doctype, self.doc.name)
			args = parent_doc.as_dict()

			if self.doc.doctype == "Leave Application":
				template = frappe.db.get_single_value('HR Settings', 'leave_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Leave Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Leave Encashment":
				template = frappe.db.get_single_value('HR Settings', 'encashment_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Encashment Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Salary Advance":
				template = frappe.db.get_single_value('HR Settings', 'advance_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Advance Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Overtime Application":
				template = frappe.db.get_single_value('HR Settings', 'overtime_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Overtime Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Employee Benefits":
				template = frappe.db.get_single_value('HR Settings', 'benefits_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Employee Benefits Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Employee Separation":
				template = frappe.db.get_single_value('HR Settings', 'employee_separation_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Employee Separation Approval Notification in HR Settings."))
					return 
			else:
				template = ""

			if not template:
				frappe.msgprint(_("Please set default template for {}.").format(self.doc.doctype))
				return
			email_template = frappe.get_doc("Email Template", template)
			message = frappe.render_template(email_template.response, args)
			# frappe.throw(self.doc.get(self.doc_approver[0]))
			self.notify({
				# for post in messages
				"message": message,
				"message_to": receipients,
				# for email
				"subject": email_template.subject
			})

	def notify_finance_users(self):
		receipients = ["finance@smcl.bt"]
		parent_doc = frappe.get_doc(self.doc.doctype, self.doc.name)
		args = parent_doc.as_dict()

		if self.doc.doctype in ("Project Capitalization"):
			template = frappe.db.get_single_value('Asset Settings', 'asset_approval_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Asset Approval Notification in Asset Settings."))
				return
		elif self.doc.doctype in ("Asset Issue Details"):
			template = frappe.db.get_single_value('Asset Settings', 'asset_issue_approval_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Asset Issue Approval Notification in Asset Settings."))
				return
		else:
			template = ""

		if not template:
			frappe.msgprint(_("Please set default template for {}.").format(self.doc.doctype))
			return
		email_template = frappe.get_doc("Email Template", template)
		message = frappe.render_template(email_template.response, args)
		# frappe.throw(self.doc.get(self.doc_approver[0]))
		self.notify({
			# for post in messages
			"message": message,
			"message_to": receipients,
			# for email
			"subject": email_template.subject
		})

	def notify_travel_administrators(self):
		receipients = []
		region = frappe.db.get_value("Employee",self.doc.employee,"region")
		if region == "Western Region":
			email_group = "Travel Adminstrator, Western Region"
		elif region == "South Western Region":
			email_group = "Travel Administrator, South Western Region"
		elif region == "Eastern Region":
			email_group = "Travel Administrator, Eastern Region"
		elif region == "Central Region":
			email_group = "Travel Administrator, Central Region"
		else:
			email_group = "Travel Administrator, CHQ"
		if self.doc.doctype == "Travel Claim":
			if self.doc.travel_type in ("Training","Meeting and Seminars","BT DAY","Pilgrimage"):
				email_group = "Travel Administrator, CHQ"
		ta = frappe.get_list("Email Group Member", filters={"email_group":email_group}, fields=['email'])
		if ta:
			receipients = [a['email'] for a in ta]
			parent_doc = frappe.get_doc(self.doc.doctype, self.doc.name)
			args = parent_doc.as_dict()
			if self.doc.doctype == "Travel Claim":
				template = frappe.db.get_single_value('HR Settings', 'claim_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Claim Approval Notification in HR Settings."))
					return
			if not template:
				frappe.msgprint(_("Please set default template for {}.").format(self.doc.doctype))
				return
			email_template = frappe.get_doc("Email Template", template)
			message = frappe.render_template(email_template.response, args)
			# frappe.throw(self.doc.get(self.doc_approver[0]))
			self.notify({
				# for post in messages
				"message": message,
				"message_to": receipients,
				# for email
				"subject": email_template.subject
			})

	def notify_ta_finance(self):
		receipients = []
		region = frappe.db.get_value("Employee",self.doc.employee,"region")
		email_group = "Travel Administrator, Finance"
		ta = frappe.get_list("Email Group Member", filters={"email_group":email_group}, fields=['email'])
		if ta:
			receipients = [a['email'] for a in ta]
			parent_doc = frappe.get_doc(self.doc.doctype, self.doc.name)
			args = parent_doc.as_dict()
			if self.doc.doctype == "Travel Claim":
				template = frappe.db.get_single_value('HR Settings', 'claim_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Claim Approval Notification in HR Settings."))
					return
			if not template:
				frappe.msgprint(_("Please set default template for {}.").format(self.doc.doctype))
				return
			email_template = frappe.get_doc("Email Template", template)
			message = frappe.render_template(email_template.response, args)
			# frappe.throw(self.doc.get(self.doc_approver[0]))
			self.notify({
				# for post in messages
				"message": message,
				"message_to": receipients,
				# for email
				"subject": email_template.subject
			})
					
	def notify(self, args):
		args = frappe._dict(args)
		# args -> message, message_to, subject
		contact = args.message_to
		if not isinstance(contact, list):
			if not args.notify == "employee":
				contact = frappe.get_doc('User', contact).email or contact

		sender      	    = dict()
		sender['email']     = frappe.get_doc('User', frappe.session.user).email
		sender['full_name'] = frappe.utils.get_fullname(sender['email'])

		try:
			frappe.sendmail(
				recipients = contact,
				sender = sender['email'],
				subject = args.subject,
				message = args.message,
			)
			frappe.msgprint(_("Email sent to {0}").format(contact))
		except frappe.OutgoingEmailError:
			pass

	def send_notification(self):
		if (self.doc.doctype not in self.field_map) or not frappe.db.exists("Workflow", {"document_type": self.doc.doctype, "is_active": 1}):
			return
		if self.new_state == "Draft":
			return
		elif self.new_state in ("Approved", "Rejected", "Cancelled", "Claimed", "Submitted"):
			if self.doc.doctype == "Material Request" and self.doc.owner != "Administrator":
				self.notify_employee()
			else:
				self.notify_employee()
		elif self.new_state.startswith("Waiting") and self.old_state != self.new_state and self.doc.doctype not in ("Asset Issue Details","Project Capitalization"):
			self.notify_approver()
		elif self.new_state.startswith("Verified") and self.old_state != self.new_state:
			self.notify_approver()
		else:
			frappe.msgprint(_("Email notifications not configured for workflow state {}").format(self.new_state))

def get_field_map():
	return {
		"Salary Advance": ["advance_approver","advance_approver_name","advance_approver_designation"],
		"Leave Encashment": ["approver","approver_name","approver_designation"],
		"Leave Application": ["leave_approver", "leave_approver_name", "leave_approver_designation"],
		"Travel Request": ["supervisor", "supervisor_name", "supervisor_designation"],
		"Travel Authorization": ["approver", "approver_name", "approver_designation"],
		"Travel Claim": ["approver", "approver_name", "approver_designation"],
		"SWS Application": ["supervisor", "supervisor_name", "supervisor_designation"],
		"SWS Membership": ["supervisor", "supervisor_name", "supervisor_designation"],
		"Employee Advance": ["advance_approver_name", "advance_approver", "advance_approver_designation"],
		"Vehicle Request": ["approver_id", "approver"],
		"Repair And Services": ["approver", "approver_name", "aprover_designation"],
		"Overtime Application": ["approver", "approver_name", "approver_designation"],
		"POL Expense": ["approver", "approver_name", "approver_designation"],
		"Material Request": ["approver","approver_name","approver_designation"],
		"Asset Movement": ["approver", "approver_name", "approver_designation"],
		"Budget Reappropiation": ["approver", "approver_name", "approver_designation"],
		"Employee Transfer": ["supervisor", "supervisor_name", "supervisor_designation"],
		"Employee Benefits": ["benefit_approver","benefit_approver_name","benefit_approver_designation"],
		"Compile Budget": ["approver","approver_name"],
		"Target Set Up": ["approver","approver_name","approver_designation"],
		"Review": ["approver","approver_name","approver_designation"],
		"Performance Evaluation": ["approver","approver_name","approver_designation"],
		"Employee Separation": ["approver","approver_name","approver_designation"],
		"POL": ["approver","approver_name","approver_designation"],
		"Contract Renewal Application": ["approver","approver_name","approver_designation"],
		"Promotion Application": ["approver","approver_name","approver_designation"],
		"Prepare Audit Plan": ["approver","approver_name","approver_designation"],
		"PMS Appeal": ["approver","approver_name","approver_designation"],
		"Asset Issue Details": [],
	}

def validate_workflow_states(doc):
	wf = CustomWorkflow(doc)
	wf.apply_workflow()

def notify_workflow_states(doc):
	wf = NotifyCustomWorkflow(doc)
	wf.send_notification()

