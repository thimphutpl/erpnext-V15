# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states


class AuditInitialReport(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.ams.doctype.audit_initial_report_checklist_item.audit_initial_report_checklist_item import AuditInitialReportChecklistItem
		from erpnext.ams.doctype.audit_initial_report_da_item.audit_initial_report_da_item import AuditInitialReportDAItem
		from erpnext.ams.doctype.audit_initial_report_team_item.audit_initial_report_team_item import AuditInitialReportTeamItem
		from frappe.types import DF

		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Link | None
		approver_name: DF.Data | None
		audit_checklist: DF.Table[AuditInitialReportChecklistItem]
		audit_engagement_letter: DF.Link | None
		audit_team: DF.Table[AuditInitialReportTeamItem]
		branch: DF.Link
		creation_date: DF.Date | None
		direct_accountability: DF.Table[AuditInitialReportDAItem]
		execute_audit_date: DF.Date | None
		execute_audit_no: DF.Link
		from_date: DF.Date
		objective_of_audit: DF.SmallText | None
		prepare_audit_plan_no: DF.Link | None
		report_status: DF.Literal["", "Pending", "Initial Report", "Follow Up", "Completed"]
		scope_of_audit: DF.SmallText | None
		status: DF.Literal["Open", "Approved", "Rejected", "Cancelled"]
		supervisor_designation: DF.Data | None
		supervisor_email: DF.Data | None
		supervisor_id: DF.Link
		supervisor_name: DF.Data | None
		to_date: DF.Date
		type: DF.Data
		workflow_state: DF.Link | None
	# end: auto-generated types
	def validate(self):
		validate_workflow_states(self)
		notify_workflow_states(self)

	def on_submit(self):
		self.update_audit_status()
		self.update_execute_checklist_item()
  
	def on_cancel(self):
		self.update_audit_status(1)
		self.update_execute_checklist_item(1)
 
	def update_audit_status(self, cancel=0):
		pap_doc = frappe.get_doc("Prepare Audit Plan", self.prepare_audit_plan_no)
		eu_doc = frappe.get_doc("Execute Audit", self.execute_audit_no)
		
		if not cancel:
			pap_doc.db_set("status", self.report_status)
			eu_doc.db_set("status", self.report_status)
		else:
			if eu_doc.docstatus == 1:
				pap_doc.db_set("status", 'Audit Execution')
				eu_doc.db_set("status", 'Exit Meeting')
			else:
				ael_doc = frappe.get_doc("Audit Engagement Letter", self.audit_engagement_letter)
				if ael_doc.docstatus == 1:
					pap_doc.db_set("status", 'Engagement Letter')
				else:
					pap_doc.db_set("status", 'Pending')
				eu_doc.db_set("status", 'Pending')
  
	def update_execute_checklist_item(self, cancel=0):
		ea = frappe.get_doc("Execute Audit", self.execute_audit_no)
		initial_report = frappe.get_doc("Audit Initial Report", self.name)

		if not cancel:
			for eaci in ea.get("audit_checklist"):
				for cl in initial_report.get("audit_checklist"):
					if cl.audit_area_checklist == eaci.audit_area_checklist and cl.observation_title == eaci.observation_title:
						eaci.db_set("status",cl.status)
						eaci.db_set("audit_remarks",cl.audit_remarks)
						eaci.db_set("auditee_remarks",cl.auditee_remarks)
		else:
			for eaci in ea.get("audit_checklist"):
				if eaci.audit_remarks or eaci.auditee_remarks:
					eaci.db_set("status",'Open')
					eaci.db_set("audit_remarks",'')
					eaci.db_set("auditee_remarks",'')

	def get_audit_checklist(self):
		data = frappe.db.sql("""
			SELECT 
				eaci.audit_area_checklist, eaci.observation_title, eaci.nature_of_irregularity, eaci.status
			FROM 
				`tabExecute Audit` ea 
			INNER JOIN
				`tabExecute Audit Checklist Item` eaci
			ON
				ea.name = eaci.parent
				AND eaci.status != 'Closed'
			WHERE			
				ea.name = '{}' 
			AND
				ea.docstatus = 1 
			ORDER BY eaci.audit_area_checklist
		""".format(self.execute_audit_no), as_dict=True)

		if not data:
			frappe.throw(_('There are no Audit Observation defined for Execute Audit No. <b>{}</b>'.format(self.execute_audit_no)))

		self.set('audit_checklist', [])
		for d in data:
			row = self.append('audit_checklist',{})
			row.update(d)
	
def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles or "Auditor" in user_roles or "Head Audit" in user_roles:
		return

	return """(
		exists(select 1
			from `tabEmployee` as e
			where e.employee = `tabAudit Initial Report`.supervisor_id
			and e.user_id = '{user}'
   			and `tabAudit Initial Report`.workflow_state in ('Waiting for Auditee Remarks','Approved'))
	)""".format(user=user)
