# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe import _
import frappe
from frappe.model.document import Document
from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states

class AuditReport(Document):
	def validate(self):
		pass
		# validate_workflow_states(self)
		# notify_workflow_states(self)

	def on_submit(self):
		self.update_audit_status()
		self.update_execute_checklist_item()
		self.notify_das()
		self.notify_supervisor()
  
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
		initial_report = frappe.get_doc("Audit Report", self.name)

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

	def get_das(self):
		receipients = []
		for member in self.direct_accountability:
			if member.employee:
				receipients.append(frappe.db.get_value("Employee", member.employee, "user_id"))
			else:
				frappe.throw("Please set User ID for employee {} in Employee Master".format(member.employee))
		return receipients

	def get_supervisors(self):
		receipients = []
		for member in self.supervisor_accountability:
			if member.supervisor:
				receipients.append(frappe.db.get_value("Employee", member.supervisor, "user_id"))
			else:
				frappe.throw("Please set User ID for Supervisor {} in Employee Master".format(item.supervisor))
		return receipients

	@frappe.whitelist()
	def notify_das(self):
		if not self.get("__islocal"):
			parent_doc = frappe.get_doc(self.doctype, self.name)
			args = parent_doc.as_dict()
		else:
			args = self.as_dict()
		receipients = []
		receipients = self.get_das()
		template = frappe.db.get_single_value('Audit Settings', 'audit_engagement_auditor_notification_template')
		if not template:
			frappe.msgprint(_("Please set default template for Audit Engagement Auditor Notification in Audit Settings."))
			return 
		email_template = frappe.get_doc("Email Template", template)
		message = frappe.render_template(email_template.response, args)
		msg = self.notify({
			# for post in messages
			"message": message,
			"message_to": receipients,
			# for email
			"subject": email_template.subject
		},1)
		# if msg != "Failed":
		# 	self.db_set("mail_sent",1)
		frappe.msgprint(msg)
	@frappe.whitelist()
	def notify_supervisor(self):
		parent_doc = frappe.get_doc(self.doctype, self.name)
		args = parent_doc.as_dict()
		receipients = []
		receipients = self.get_supervisors()
		template = frappe.db.get_single_value('Audit Settings', 'audit_engagement_supervisor_notification_template')
		if not template:
			frappe.msgprint(_("Please set default template for Audit Engagement Supervisor Notification in Audit Settings."))
			return 
		email_template = frappe.get_doc("Email Template", template)
		message = frappe.render_template(email_template.response, args)
		msg = self.notify({
			# for post in messages
			"message": message,
			"message_to": receipients,
			# for email
			"subject": email_template.subject
		},1)
		# if msg != "Failed":
		# 	self.db_set("mail_sent",1)
		frappe.msgprint(msg)

	def notify(self, args, approver = 0):
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
			if approver == 0:
				frappe.msgprint(_("Email sent to {0}").format(contact))
			else:
				return _("Email sent to {0}").format(contact)
		except frappe.OutgoingEmailError:
			pass

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
			auditor_display = auditee_display = 1
		if frappe.session.user in auditors:
			auditor_display = 1
		if frappe.session.user in auditees:
			auditee_display = 1
		return auditor_display, auditee_display

	@frappe.whitelist()
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
			where e.employee = `tabAudit Report`.supervisor_id
			and e.user_id = '{user}'
   			and `tabAudit Report`.workflow_state in ('Waiting for Auditee Remarks','Approved'))
	)""".format(user=user)

