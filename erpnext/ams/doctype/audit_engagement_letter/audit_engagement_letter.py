# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states
from frappe import _


class AuditEngagementLetter(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.ams.doctype.audit_engagement_letter_item.audit_engagement_letter_item import AuditEngagementLetterItem
		from frappe.types import DF

		amended_from: DF.Link | None
		audit_team: DF.Table[AuditEngagementLetterItem]
		branch: DF.Link | None
		from_date: DF.Date
		message: DF.TextEditor
		posting_date: DF.Date | None
		prepare_audit_plan_no: DF.Link
		reference_date: DF.Date
		remarks: DF.SmallText | None
		status: DF.Literal["Open", "Confirmed", "Rejected", "Cancelled"]
		subject: DF.Data
		supervisor_designation: DF.Data | None
		supervisor_email: DF.Data | None
		supervisor_id: DF.Link | None
		supervisor_name: DF.Data | None
		to_date: DF.Date
		type: DF.Data
		workflow_state: DF.Link | None
	# end: auto-generated types
	def validate(self):
		self.get_message_template()
		if self.auditor_email_sent == 0 and self.docstatus == 0:
			self.notify_auditors()
			self.auditor_email_sent = 1
   
	def on_submit(self):
		self.update_engagement_letter_no()
		row = 1
		for a in self.audit_team:
			if not a.declaration or a.declaration == "" or a.declaration == " ":
				frappe.throw("Declaration not set for Auditor {} at row {}".format(str(a.employee)+": "+str(a.employee_name), row))
			row += 1
		# self.notify_auditors()
  
	def on_cancel(self):
		self.update_engagement_letter_no(1)
 
	def update_engagement_letter_no(self, cancel=0):
		pap_doc = frappe.get_doc("Prepare Audit Plan", self.prepare_audit_plan_no)
		if not cancel:
			pap_doc.db_set("audit_engagement_letter", self.name)
			pap_doc.db_set("status", 'Engagement Letter')
		else:
			pap_doc.db_set("audit_engagement_letter", '')
			pap_doc.db_set("status", 'Pending')

	def get_auditors(self):
		receipients = []
		for member in self.audit_team:
			if member.auditor_email:
				receipients.append(member.auditor_email)
			else:
				frappe.throw("Please set User ID for auditor {} in Employee Master".format(member.employee))
		return receipients

	def get_cc(self):
		receipients = []
		for member in self.cc_item:
			if frappe.db.get_value("Employee", member.employee, "user_id"):
				receipients.append(frappe.db.get_value("Employee", member.employee, "user_id"))
			else:
				frappe.throw("Please set User ID for Employee {} in Employee Master".format(member.employee))
		return receipients

	@frappe.whitelist()
	def get_message_template(self):
		self.message = ""
		cc_message = audit_team_str = checklist = ""
		audit_teams = audit_team_roles = []
		pap = frappe.get_doc("Prepare Audit Plan", self.prepare_audit_plan_no)
		audit_team_roles.append(ar.role for ar in self.audit_team)
		if "Lead Auditor" in set(audit_team_roles):
			audit_team_str = "led by"
		else:
			audit_team_roles = "comprising of"
		audit_team_str += ", ".join(frappe.db.get_value("Employee", aud.employee, "employee_name")+" ("+aud.audit_role+")" for aud in self.audit_team)
		if len(pap.audit_checklist) > 0:
			checklist = "<table>"
			checklist += "<tr><th>Audit Checklist</th><th>Audit Area</th><th>Type of Audit</th><tr>"
			for cl in pap.audit_checklist:
				checklist += f"<tr><td>{cl.audit_area_checklist}</td><td>{cl.audit_criteria}</td><td>{cl.type_of_audit}</td></tr>"
			checklist += "</table>"
		if self.type:
			self.message = str(frappe.db.get_value("Audit Type", self.type, "template")).format(subject=self.subject, salutation="Sir", audit_team=audit_team_str, date_range="", criteria=checklist, creator=frappe.db.get_value("User", self.owner, "full_name"), designation=frappe.db.get_value("Employee", {"user_id": self.owner}, "designation"))
			# self.message = str(frappe.db.get_value("Audit Type", self.type, "template")).format(subject="", salutation="", audit_team="", date_range="", criteria="", creator="", designation="")
		else:
			self.message = None

		cc_message = "cc.<br> 1. Auditing team for compliance.<br>"
		if len(self.cc_item) > 0:
			count = 2
			gms = []
			for a in self.cc_item:
				if a.designation == "General Manager":
					gms.append(a.department)
			for a in self.cc_item:
				if a.designation == "Chief Executive Officer":
					cc_message += str(count)+". The "+str(a.designation)+" .BDBL, Thimphu"+a.remarks+"<br>"
					count += 1
			if len(gms) > 1:
				cc_message += str(count)+". The General Manager(s) ("+(", ".join(g for g in gms))+")BDBL, Thimphu for kind information.<br>"
				count += 1
			cc_message += str(count)+". Office copy"
			self.message += cc_message



	@frappe.whitelist()
	def notify_auditors(self):
		if not self.get("__islocal"):
			parent_doc = frappe.get_doc(self.doctype, self.name)
			args = parent_doc.as_dict()
		else:
			args = self.as_dict()
		receipients = []
		receipients = self.get_auditors()
		# template = frappe.db.get_single_value('Audit Settings', 'audit_engagement_auditor_notification_template')
		template = self.message
		if not template:
			frappe.throw(_("Message Template cannot be blank. Perhaps message template is not set in Audit Type {}".format(rappe.get_desk_link("Audit Type", self.audit_type))))
			return 
		# email_template = frappe.get_doc("Email Template", template)
		# message = frappe.render_template(email_template.response, args)
		message = frappe.render_template(template, args)
		msg = self.notify({
			# for post in messages
			"message": message,
			"message_to": receipients,
			# for email
			"subject": self.subject
		},1)
		# if msg != "Failed":
		# 	self.db_set("mail_sent",1)
		frappe.msgprint(msg)

	@frappe.whitelist()
	def notify_cc(self):
		if not self.get("__islocal"):
			parent_doc = frappe.get_doc(self.doctype, self.name)
			args = parent_doc.as_dict()
		else:
			args = self.as_dict()
		receipients = []
		receipients = self.get_cc()
		# template = frappe.db.get_single_value('Audit Settings', 'audit_engagement_auditor_notification_template')
		template = self.message
		if not template:
			frappe.throw(_("Message Template cannot be blank. Perhaps message template is not set in Audit Type {}".format(rappe.get_desk_link("Audit Type", self.audit_type))))
			return 
		# email_template = frappe.get_doc("Email Template", template)
		# message = frappe.render_template(email_template.response, args)
		message = frappe.render_template(template, args)
		msg = self.notify({
			# for post in messages
			"message": message,
			"message_to": receipients,
			# for email
			"subject": self.subject
		},1)
		# if msg != "Failed":
		# 	self.db_set("mail_sent",1)
		frappe.msgprint(msg)

	@frappe.whitelist()
	def notify_supervisor(self):
		parent_doc = frappe.get_doc(self.doctype, self.name)
		args = parent_doc.as_dict()
		supervisor_email = frappe.db.get_value("Employee", self.supervisor_id, "user_id")
		receipients = [supervisor_email]
		template = self.message
		if not template:
			frappe.throw(_("Message Template cannot be blank. Perhaps message template is not set in Audit Type {}".format(rappe.get_desk_link("Audit Type", self.audit_type))))
			return 
		# email_template = frappe.get_doc("Email Template", template)
		email_template = self.message
		message = frappe.render_template(email_template, args)
		msg = self.notify({
			# for post in messages
			"message": message,
			"message_to": receipients,
			# for email
			"subject": self.subject
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
				frappe.msgprint(_("Email sent to {0}").format(", ".join(a for a in contact)))
			else:
				return _("Email sent to {0}").format(", ".join(a for a in contact))
		except frappe.OutgoingEmailError:
			pass

	# Get audit tean from Prepare Audit Plan
	@frappe.whitelist()
	def get_audit_team(self):
		data = frappe.db.sql("""
			SELECT 
				papi.employee,
				papi.employee_name,
				papi.designation,
				papi.audit_role
			FROM 
				`tabPrepare Audit Plan` pap 
			INNER JOIN
				`tabPAP Audit Team Item` papi
			ON
				pap.name = papi.parent			
			WHERE			
				pap.name = '{}' 
			AND
				pap.docstatus = 1 
			ORDER BY papi.idx
		""".format(self.prepare_audit_plan_no), as_dict=True)

		if not data:
			frappe.throw(_('There are no Audit Team defined for Prepare Audit Plan No. <b>{}</b>'.format(self.prepare_audit_plan_no)))

		self.set('audit_team', [])
		for d in data:
			row = self.append('audit_team',{})
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
			where e.employee = `tabAudit Engagement Letter`.supervisor_id
			and e.user_id = '{user}'
		)
	)""".format(user=user)
