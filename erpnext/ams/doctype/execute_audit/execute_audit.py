# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from ast import Pass
from ast import Pass
import frappe
from frappe import _
from frappe.utils import flt,nowdate
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states

class ExecuteAudit(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.ams.doctype.direct_accountability_item.direct_accountability_item import DirectAccountabilityItem
		from erpnext.ams.doctype.direct_accountability_supervisor_item.direct_accountability_supervisor_item import DirectAccountabilitySupervisorItem
		from erpnext.ams.doctype.execute_audit_checklist_item.execute_audit_checklist_item import ExecuteAuditChecklistItem
		from erpnext.ams.doctype.execute_audit_team_item.execute_audit_team_item import ExecuteAuditTeamItem
		from frappe.types import DF

		amended_from: DF.Link | None
		audit_checklist: DF.Table[ExecuteAuditChecklistItem]
		audit_engagement_letter: DF.Link | None
		audit_team: DF.Table[ExecuteAuditTeamItem]
		branch: DF.Link
		direct_accountability: DF.Table[DirectAccountabilityItem]
		from_date: DF.Date
		iain_number: DF.Data | None
		objective_of_audit: DF.SmallText | None
		posting_date: DF.Date | None
		prepare_audit_plan_no: DF.Link
		reference_date: DF.Date | None
		scope_of_audit: DF.SmallText | None
		status: DF.Literal["", "Pending", "Exit Meeting", "Initial Report", "Follow Up", "Closed"]
		supervisor_accountability: DF.Table[DirectAccountabilitySupervisorItem]
		supervisor_designation: DF.Data | None
		supervisor_email: DF.Data | None
		supervisor_id: DF.Link
		supervisor_name: DF.Data | None
		to_date: DF.Date
		type: DF.Data
		workflow_state: DF.Link | None
		workflow_status: DF.Literal["Open", "Assigned", "Rejected", "Cancelled"]
	# end: auto-generated types
	def validate(self):
		pass
		# if self.workflow_state == 'Assigned':
		# 	self.validate_accountability_assigner()
		# validate_workflow_states(self)
		# notify_workflow_states(self)

	def on_submit(self):
		self.update_status()
  
	def on_cancel(self):
		self.update_status(1)

	def on_update(self):
		self.update_direct_accountability()

	def update_direct_accountability(self):
		for item in self.direct_accountability:
			#---------Audit Initial Report---------
			for air in frappe.db.sql("""
                            select name from `tabAudit Initial Report DA Item`
                            where child_ref = '{}' and docstatus < 2
                            """.format(item.name),as_dict=1):
				frappe.db.sql("""
                  update `tabAudit Report DA Item` set checklist = '{}',
                  observation_title = '{}',
                  observation = '{}',
                  employee = '{}',
                  employee_name = '{}',
                  designation = '{}'
                  where name = '{}'
                  """.format(item.checklist, item.observation_title, item.observation, item.employee, item.employee_name, item.designation, air.name))
			#----------Follow Up------------
			for fu in frappe.db.sql("""
                            select name from `tabFollow Up DA Item`
                            where child_ref = '{}' and docstatus < 2
                            """.format(item.name),as_dict=1):
				frappe.db.sql("""
                  update `tabFollow Up DA Item` set checklist = '{}',
                  observation_title = '{}',
                  observation = '{}',
                  employee = '{}',
                  employee_name = '{}',
                  designation = '{}'
                  where name = '{}'
                  """.format(item.checklist, item.observation_title, item.observation, item.employee, item.employee_name, item.designation, fu.name))
			#----------Close Follow Up------------
			for cfu in frappe.db.sql("""
                            select name from `tabDirect Accountability Item`
                            where child_ref = '{}' and docstatus < 2 and parenttype = 'Close Follow Up'
                            """.format(item.name),as_dict=1):
				frappe.db.sql("""
                  update `tabAudit Report DA Item` set checklist = '{}',
                  observation_title = '{}',
                  observation = '{}',
                  employee = '{}',
                  employee_name = '{}',
                  designation = '{}'
                  where name = '{}'
                  """.format(item.checklist, item.observation_title, item.observation, item.employee, item.employee_name, item.designation, cfu.name))

		for s_item in self.supervisor_accountability:
			#Updating every reference since all the related doctypes use common child table Direct Accountability Supervisor Item
			for sda in frappe.db.sql("""
                            select name from `tabDirect Accountability Supervisor Item`
                            where child_ref = '{}' and docstatus < 2 and parenttype != 'Execute Audit'
                            """.format(s_item.name),as_dict=1):
				frappe.db.sql("""
                  update ``Direct Accountability Supervisor Item` set checklist = '{}',
                  observation_title = '{}',
                  observation = '{}',
                  employee = '{}',
                  employee_name = '{}',
                  designation = '{}'
                  where name = '{}'
                  """.format(s_item.checklist, s_item.observation_title, s_item.observation, s_item.supervisor, s_item.supervisor_name, s_item.designation, sda.name))

	#To display declaration field/create draft report button based on auditor logged in
	@frappe.whitelist()
	def check_auditor_and_audit_report(self):
		display = audit_report = 0
		for auditor in self.audit_team:
			if frappe.session.user == frappe.db.get_value("Employee",auditor.employee,"user_id"):
				display = 1
		if frappe.db.exists("Audit Report", {"execute_audit_no": self.name, "docstatus": 1}):
			audit_report = 1
		return display, audit_report

	@frappe.whitelist()
	def get_auditor_and_auditee(self):
		auditor_display = auditee_display = 0
		auditors = []
		auditees = []
		for auditor in self.audit_team:
			auditors.append(frappe.db.get_value("Employee", auditor.employee, "user_id"))
		for auditee_emp in self.direct_accountability:
			auditees.append(frappe.db.get_value("Employee", auditee_emp.employee, "user_id"))
		for auditee_sup in self.supervisor_accountability:
			auditees.append(frappe.db.get_value("Employee", auditee_sup.supervisor, "user_id"))
		if frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles(frappe.session.user):
			auditor_display = auditee_display = 1
		if frappe.session.user in auditors:
			auditor_display = 1
		if frappe.session.user in auditees:
			auditee_display = 1
		return auditor_display, auditee_display

	@frappe.whitelist()
	def validate_accountability_assigner(self):
		auditors = []
		for auditor in self.audit_team:
			auditors.append(frappe.db.get_value("Employee", auditor.employee, "user_id"))
		if frappe.session.user != self.supervisor_email:
			if frappe.session.user not in auditors:
				frappe.throw("Only <b>{}</b> or Auditors: {} can Assign Direct Accountability for this request".format(self.supervisor_name, ", ".join(a for a in auditors)))
			
	def update_status(self, cancel=0):
		pap = frappe.get_doc("Prepare Audit Plan", self.prepare_audit_plan_no)
		execute_audit = frappe.get_doc("Execute Audit", self.name)
		if not cancel:
			pap.db_set("status", 'Audit Execution')
			execute_audit.db_set("status", 'Exit Meeting')
			for cl in execute_audit.get("audit_checklist"):
				if cl.nature_of_irregularity in ('For Information','Found in order','Resolved'):
					cl.db_set("status", 'Closed')
		else:
			pap.db_set("status", 'Engagement Letter')
			execute_audit.db_set("status", 'Pending')
			for cl in execute_audit.get("audit_checklist"):
				if cl.nature_of_irregularity in ('Observation','Unresolved','Un-Reconciled'):
					cl.db_set("status", 'Open')

	@frappe.whitelist()
	def get_audit_team(self):
		data = frappe.db.sql("""
			SELECT 
				papi.employee, papi.employee_name, papi.designation, papi.audit_role
			FROM 
				`tabPrepare Audit Plan` pap 
			INNER JOIN
				`tabPAP Audit Team Item` papi
			ON
				pap.name = papi.parent
			WHERE			
				pap.name = '{}' AND pap.docstatus = 1 
			ORDER BY papi.idx
		""".format(self.prepare_audit_plan_no), as_dict=True)

		if not data:
			frappe.throw(_('There are no Audit Team defined for Prepare Audit Plan No. <b>{}</b>'.format(self.prepare_audit_plan_no)))

		self.set('audit_team', [])
		for d in data:
			row = self.append('audit_team',{})
			row.update(d)
	
	@frappe.whitelist()
	def get_checklist(self):
		data = frappe.db.sql("""
			SELECT 
				papi.audit_area_checklist, 'Open' status
			FROM 
				`tabPrepare Audit Plan` pap 
			INNER JOIN
				`tabPAP Checklist Item` papi
			ON
				pap.name = papi.parent
			WHERE
				pap.name = '{}' AND pap.docstatus = 1 
			ORDER BY papi.audit_area_checklist
		""".format(self.prepare_audit_plan_no), as_dict=True)

		if not data:
			frappe.throw(_('There are no Checklist defined for Prepare Audit Plan No. <b>{}</b>'.format(self.prepare_audit_plan_no)))

		self.set('audit_checklist', [])
		for d in data:
			row = self.append('audit_checklist',{})
			row.update(d)

	@frappe.whitelist()
	def get_observation(self):
		data = frappe.db.sql("""
			select 
				audit_area_checklist as checklist, observation_title, observation
			from 
				`tabExecute Audit Checklist Item`
			where 
				parent = '{0}' and nature_of_irregularity not in ('For Information','Found in order','Resolved')
			order by audit_area_checklist
		""".format(self.name), as_dict=True)

		if not data:
			frappe.throw(_('There are no Observation defined for Execute Audit: <b>{}</b>'.format(self.name)))

		self.set('direct_accountability', [])
		for d in data:
			row = self.append('direct_accountability',{})
			row2 = self.append('supervisor_accountability', {})
			row2.update(d)
			row.update(d)
   
@frappe.whitelist()
def create_initial_report(source_name, target_doc=None):
	doclist = get_mapped_doc("Execute Audit", source_name, {
		"Execute Audit": {
			"doctype": "Audit Report",
			"field_map": {
				"execute_audit_no": "name",
				"execute_audit_date": "posting_date",
				"audit_team": "audit_team",
				"audit_checklist": "audit_checklist",
			}
		},
		"Direct Accountability Item": {
					"doctype": "Audit Initial Report DA Item",
					"field_map": [
						["child_ref", "name"],
					]
				},
		"Direct Accountability Supervisor Item": {
					"doctype": "Direct Accountability Supervisor Item",
					"field_map": [
						["child_ref", "name"],
					]
				},
	}, target_doc)

	return doclist

@frappe.whitelist()
def create_follow_up(source_name, target_doc=None):
	doclist = get_mapped_doc("Execute Audit", source_name, {
		"Execute Audit": {
			"doctype": "Follow Up",
			"field_map": {
				"execute_audit_no": "name",
				"execute_audit_date": "posting_date",
				"audit_team": "audit_team",
				"audit_checklist": "audit_checklist",
			}
		},
		"Direct Accountability Item": {
					"doctype": "Follow Up DA Item",
					"field_map": [
						["child_ref", "name"],
					]
				},
		"Direct Accountability Supervisor Item": {
					"doctype": "Direct Accountability Supervisor Item",
					"field_map": [
						["child_ref", "name"],
					]
				},
	}, target_doc)

	return doclist

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles or "Auditor" in user_roles:
		return

	return """(
		`tabExecute Audit`.owner = '{user}'
		or
		exists(select 1
			from `tabEmployee`
			where `tabEmployee`.name = `tabExecute Audit`.supervisor_id
			and `tabEmployee`.user_id = '{user}')
		)""".format(user=user)
