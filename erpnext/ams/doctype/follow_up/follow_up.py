# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from wsgiref import validate
import frappe
from frappe import _
from frappe.utils import flt,nowdate
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from erpnext.custom_utils import sendmail

class FollowUp(Document):		
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.ams.doctype.direct_accountability_supervisor_item.direct_accountability_supervisor_item import DirectAccountabilitySupervisorItem
		from erpnext.ams.doctype.follow_up_audit_team_item.follow_up_audit_team_item import FollowUpAuditTeamItem
		from erpnext.ams.doctype.follow_up_checklist_item.follow_up_checklist_item import FollowUpChecklistItem
		from erpnext.ams.doctype.follow_up_da_item.follow_up_da_item import FollowUpDAItem
		from frappe.types import DF

		amended_from: DF.Link | None
		audit_engagement_letter: DF.Link | None
		audit_observations: DF.Table[FollowUpChecklistItem]
		audit_team: DF.Table[FollowUpAuditTeamItem]
		auditor_designation: DF.Data | None
		auditor_name: DF.Data | None
		branch: DF.Link
		cflg_follow_up: DF.Check
		direct_accountability: DF.Table[FollowUpDAItem]
		execute_audit_no: DF.Link
		follow_up_by: DF.Link | None
		from_date: DF.Date | None
		iain_number: DF.Data | None
		objective_of_audit: DF.SmallText | None
		posting_date: DF.Date | None
		prepare_audit_plan_no: DF.Link | None
		reference_date: DF.Date | None
		scope_of_audit: DF.SmallText | None
		supervisor_accountability: DF.Table[DirectAccountabilitySupervisorItem]
		supervisor_designation: DF.Data | None
		supervisor_email: DF.Data | None
		supervisor_id: DF.Link | None
		supervisor_name: DF.Data | None
		to_date: DF.Date | None
		type: DF.Data
	# end: auto-generated types
	def on_submit(self):
		self.update_execute_audit_status()
		self.update_execute_checklist_item()
		self.notify_audit_and_auditee()
  
	def on_cancel(self):
		self.update_execute_audit_status(1)
		self.update_execute_checklist_item(1)
 
	def on_update_after_submit(self):
		self.on_update_checklist_item()
		self.notify_audit_and_auditee()

	def update_execute_audit_status(self, cancel=0):
		pap_doc = frappe.get_doc("Prepare Audit Plan", self.prepare_audit_plan_no)
		eu_doc = frappe.get_doc("Execute Audit", self.execute_audit_no)
		
		if not cancel:
			pap_doc.db_set("status",'Follow Up')
			eu_doc.db_set("status", 'Follow Up')
		else:
			initial_doc = frappe.get_doc("Audit Report", {"execute_audit_no": self.execute_audit_no})
			if initial_doc.docstatus == 1:
				pap_doc.db_set("status", 'Initial Report')
				eu_doc.db_set("status", 'Initial Report')
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
  
	def on_update_checklist_item(self):
		ea = frappe.get_doc("Execute Audit", self.execute_audit_no)
		follow_up = frappe.get_doc("Follow Up", self.name)
  
		for eaci in ea.get("audit_checklist"):
			for cl in follow_up.get("audit_observations"):
				if cl.audit_area_checklist == eaci.audit_area_checklist and cl.observation_title == eaci.observation_title:
					if eaci.status == 'Follow Up':
						eaci.db_set("status",'Replied')
					if cl.status == "Reply":						
						cl.db_set("status",'Replied')

	def update_execute_checklist_item(self, cancel=0):
		ea = frappe.get_doc("Execute Audit", self.execute_audit_no)
		follow_up = frappe.get_doc("Follow Up", self.name)

		for eaci in ea.get("audit_checklist"):
			for cl in follow_up.get("audit_observations"):
				if cl.audit_area_checklist == eaci.audit_area_checklist and cl.observation_title == eaci.observation_title:		
					if not cancel:
						if eaci.status == 'Open' and cl.audit_remarks:
							eaci.db_set("status", 'Follow Up')
							cl.db_set("status", 'Reply')						
					else:
						eaci.db_set("status", 'Open')
						cl.db_set("status", 'Follow Up')

	@frappe.whitelist()
	def get_message_template(self):
		if self.type:
			if frappe.db.get_value("Audit Type", self.type, "template") != None:
				self.message = frappe.db.get_value("Audit Template", self.type, "template")
	
	@frappe.whitelist()		
	def notify_audit_and_auditee(self):
		now_date = nowdate()
		query = """
			select 
				fuci.audit_area_checklist, fuci.observation_title, fuci.nature_of_irregularity, fuci.status, fuci.audit_remarks, fuci.auditee_remarks
			from `tabFollow Up` fu, `tabFollow Up Checklist Item` fuci where fu.name=fuci.parent and fu.name = '{}' and fu.docstatus=1
		""".format(self.name)
		data = frappe.db.sql(query, as_dict=True)

		if frappe.session.user == self.owner:
			subject = 'Audit Follow Up'
			msg = ''' 
					<p>Follow Up ID: {}</p>
					<table border=1 style='border-collapse: collapse;'>
						<tr>
							<th>Audit Area Checklist</th>
							<th>Observation Title</th>
							<th>Nature of Irregularity</th>
							<th>Status</th>
							<th>Audit Remarks</th>
							<th>Auditee Remarks</th>
						</tr>
					'''.format(self.name)
			for d in data:
				msg += '''
					<tr>
						<td>{}</td>
						<td>{}</td>
						<td>{}</td>
						<td>{}</td>
						<td>{}</td>
						<td>{}</td>
						</tr>
					'''.format(d.audit_area_checklist, d.observation_title , d.nature_of_irregularity, d.status, d.audit_remarks , d.auditee_remarks) 
			msg += '</table>'
			recipent = self.supervisor_email
			
			if data:
				sendmail(recipent,subject,msg)

		elif frappe.session.user == self.supervisor_email:
			subject = 'Audit Follow Up Reply'
			msg = ''' 
					<p>Follow Up ID: {}</p>
					<table border=1 style='border-collapse: collapse;'>
						<tr>
							<th>Audit Area Checklist</th>
							<th>Observation Title</th>
							<th>Nature of Irregularity</th>
							<th>Status</th>
							<th>Audit Remarks</th>
							<th>Auditee Remarks</th>
						</tr>
					'''.format(self.name)
			for d in data:
				msg += '''
					<tr>
						<td>{}</td>
						<td>{}</td>
						<td>{}</td>
						<td>{}</td>
						<td>{}</td>
						<td>{}</td>
						</tr>
					'''.format(d.audit_area_checklist, d.observation_title , d.nature_of_irregularity, d.status, d.audit_remarks , d.auditee_remarks) 
			msg += '</table>'
			recipent = self.owner
			
			if data:
				sendmail(recipent,subject,msg)

	@frappe.whitelist()		
	def get_observations(self):
		data = frappe.db.sql("""
			SELECT 
				eaci.audit_area_checklist, eaci.observation_title, eaci.observation, eaci.nature_of_irregularity, 'Follow Up' status
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
			ORDER BY eaci.idx
		""".format(self.execute_audit_no), as_dict=True)

		if not data:
			frappe.throw(_('There are no Audit Observation defined for Execute Audit No. <b>{}</b>'.format(self.execute_audit_no)))

		self.set('audit_observations', [])
		for d in data:
			row = self.append('audit_observations',{})
			row.update(d)

	@frappe.whitelist()
	def get_auditor_and_auditee(self):
		auditor_display = auditee_display = 0
		auditors = auditees = []
		for auditor in self.audit_team:
			auditors.append(frappe.db.get_value("Employee", auditor.employee, "user_id"))
		for auditee_emp in self.direct_accountability:
			auditees.append(frappe.db.get_value("Employee", auditee_emp.employee, "user_id"))
		for auditee_sup in self.supervisor_accountability:
				auditees.append(frappe.db.get_value("Employee", auditee_sup.supervisor, "user_id"))
		if frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles(frappe.session.user):
			auditor_display = 1
			auditee_display = 1
		if frappe.session.user in auditors:
			auditor_display = 1
		if frappe.session.user in auditees:
			auditee_display = 1
		return auditor_display, auditee_display

	@frappe.whitelist()		
	def get_direct_accountability(self):
		old_doc = frappe.get_doc("Execute Audit", self.execute_audit_no)
		self.set('direct_accountability', [])
		self.set('supervisor_accountability', [])
		for a in old_doc.get("audit_checklist"):
			for b in old_doc.get("direct_accountability"):
				if a.audit_area_checklist == b.checklist and a.observation_title == b.observation_title:
					if a.status != "Closed":
						row = self.append('direct_accountability',{})
						row.checklist  = b.checklist
						row.observation_title  = b.observation_title
						row.observation  = b.observation
						row.employee  = b.employee
						row.employee_name  = b.employee_name
						row.designation  = b.designation
						row.child_ref = b.name
			for c in old_doc.get("supervisor_accountability"):
				if a.audit_area_checklist == c.checklist and a.observation_title == c.observation_title:
					if a.status != "Closed":
						row = self.append('direct_accountability',{})
						row.checklist  = c.checklist
						row.observation_title  = c.observation_title
						row.observation  = c.observation
						row.employee  = c.supervisor
						row.employee_name  = c.supervisor_name
						row.designation  = c.designation
						row.child_ref = c.name


@frappe.whitelist()
def create_close_follow_up(source_name, target_doc=None):
	doclist = get_mapped_doc("Follow Up", source_name, {
		"Follow Up": {
			"doctype": "Close Follow Up",
			"field_map": {
				"follow_up_no": "name",
				"audit_team": "audit_team"
			}

		},
		"Follow Up DA Item": {
					"doctype": "Direct Accountability Item",
					"field_map": [
						["child_ref", "child_ref"],
					]
				},
		"Direct Accountability Supervisor Item": {
					"doctype": "Direct Accountability Supervisor Item",
					"field_map": [
						["child_ref", "child_ref"],
					]
				},
	}, target_doc)

	return doclist

def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles or "Auditor" in user_roles:
		return

	return """(
		exists(select 1
			from `tabEmployee` as e
			where e.employee = `tabFollow Up`.supervisor_id
			and e.user_id = '{user}')
		or
		exists(select 1
			from `tabEmployee` as e, `tabFollow Up DA Item` as f
			where f.parent = `tabFollow Up`.name
   			and e.employee = f.employee
			and e.user_id = '{user}')
	)""".format(user=user)

