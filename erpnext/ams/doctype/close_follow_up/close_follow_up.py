# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe import _
from frappe.model.document import Document

class CloseFollowUp(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.ams.doctype.close_follow_up_audit_team_item.close_follow_up_audit_team_item import CloseFollowUpAuditTeamItem
		from erpnext.ams.doctype.close_follow_up_checklist_item.close_follow_up_checklist_item import CloseFollowUpChecklistItem
		from erpnext.ams.doctype.direct_accountability_item.direct_accountability_item import DirectAccountabilityItem
		from erpnext.ams.doctype.direct_accountability_supervisor_item.direct_accountability_supervisor_item import DirectAccountabilitySupervisorItem
		from frappe.types import DF

		amended_from: DF.Link | None
		audit_engagement_letter: DF.Link | None
		audit_observations: DF.Table[CloseFollowUpChecklistItem]
		audit_team: DF.Table[CloseFollowUpAuditTeamItem]
		auditor_designation: DF.Data | None
		auditor_name: DF.Data | None
		branch: DF.Link
		creation_date: DF.Date | None
		direct_accountability: DF.Table[DirectAccountabilityItem]
		execute_audit_no: DF.Link | None
		follow_up_by: DF.Link | None
		follow_up_no: DF.Link
		from_date: DF.Date | None
		iain_number: DF.Data | None
		objective_of_audit: DF.SmallText | None
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
		self.update_follow_up()
		self.update_execute_audit()
		self.update_execute_audit_status()
  
	def on_cancel(self):
		# self.update_cflg_follow_up(1)
		self.update_follow_up(1)
		self.update_execute_audit(1)
		self.update_execute_audit_status(1)
	
	def update_follow_up(self, cancel=0):
		follow_up = frappe.get_doc("Follow Up", self.follow_up_no)
		close_follow_up = frappe.get_doc("Close Follow Up", self.name)
  
		for fu in follow_up.get("audit_observations"):
			for cfu in close_follow_up.get("audit_observations"):
				if fu.audit_area_checklist == cfu.audit_area_checklist and fu.observation_title == cfu.observation_title:
					if not cancel:
						fu.db_set("status", cfu.status, commit=True)
					else:
						fu.db_set("status", "Replied", commit=True)

	def update_execute_audit(self,cancel=0):
		execute_audit = frappe.get_doc("Execute Audit", self.execute_audit_no)
		close_follow_up = frappe.get_doc("Close Follow Up", self.name)
  
		for ea in execute_audit.get("audit_checklist"):
			for cfu in close_follow_up.get("audit_observations"):
				if ea.audit_area_checklist == cfu.audit_area_checklist and ea.observation_title == cfu.observation_title:
					if not cancel:
						ea.db_set("status", cfu.status, commit=True)
						ea.db_set("audit_remarks", cfu.audit_remarks, commit=True)
						ea.db_set("auditee_remarks", cfu.auditee_remarks, commit=True)
					else:
						ea.db_set("status", "Replied", commit=True)
						ea.db_set("audit_remarks", '', commit=True)
						ea.db_set("auditee_remarks", '', commit=True)
	
	def update_execute_audit_status(self, cancel=0):
		pap_doc = frappe.get_doc("Prepare Audit Plan", self.prepare_audit_plan_no)
		eu_doc = frappe.get_doc("Execute Audit", self.execute_audit_no)
		fu_doc = frappe.get_doc("Follow Up", self.follow_up_no)
		
		if not cancel:
			flag = 0
			for fu in fu_doc.get("audit_observations"):
				if fu.status != 'Closed':
					flag = 1

			if flag == 0:
				pap_doc.db_set("status",'Closed')
				eu_doc.db_set("status", 'Closed')
		else:
			fu_doc = frappe.get_doc("Follow Up", self.follow_up_no)
			if fu_doc.docstatus == 1:
				pap_doc.db_set("status", 'Follow Up')
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

	@frappe.whitelist()
	def get_auditor_and_auditee(self):
		auditor_display = auditee_display = 0
		auditors = auditees = []
		for auditor in self.audit_team:
			auditors.append(frappe.db.get_value("Employee", auditor.employee, "user_id"))
		for auditee_emp in self.direct_accountability:
			auditees.append(frappe.db.get_vlue("Employee", auditee_emp.employee, "user_id"))
		for auditee_sup in self.supervisor_accountability:
				auditees.append(frappe.db.get_vlue("Employee", auditee_sup.employee, "user_id"))
		if frappe.session.user == "Administrator":
			auditor_display = auditee_display = 1
		if frappe.session.user in auditors:
			auditor_display = 1
		if frappe.session.user in auditees:
			auditee_display = 1
		return auditor_display, auditee_display

	@frappe.whitelist()		
	def get_checklist(self):
		data = frappe.db.sql("""
			SELECT 
				b.audit_area_checklist, b.observation_title, b.nature_of_irregularity, 'Closed' status, b.audit_remarks, b.auditee_remarks
			FROM 
				`tabFollow Up` a
			INNER JOIN
				`tabFollow Up Checklist Item` b
			ON
				a.name = b.parent
			WHERE			
				a.name = '{}' and b.status not in ('For Information','Found in order','Resolved', 'Closed')
			AND
				a.docstatus = 1 
			ORDER BY b.idx
		""".format(self.follow_up_no), as_dict=True)

		if not data:
			frappe.throw(_('There are no Checklist defined for Follow Up No. <b>{}</b>'.format(self.follow_up_no)))

		self.set('audit_observations', [])
		for d in data:
			row = self.append('audit_observations',{})
			row.update(d)
