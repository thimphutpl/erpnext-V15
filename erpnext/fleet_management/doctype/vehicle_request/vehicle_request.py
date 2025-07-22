# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _, whitelist
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, get_datetime, nowdate, cint, datetime, date_diff, time_diff, get_fullname
from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states
from hrms.utils import get_employee_email

class VehicleRequest(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.vehicle_request_employee.vehicle_request_employee import VehicleRequestEmployee
		from erpnext.fleet_management.doctype.vehicle_request_item.vehicle_request_item import VehicleRequestItem
		from frappe.types import DF

		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Data | None
		approver_name: DF.Data | None
		branch: DF.Link | None
		contact_number: DF.Data | None
		cost_center: DF.Link | None
		designation: DF.ReadOnly | None
		driver: DF.Data | None
		driver_name: DF.Data | None
		employee: DF.Link
		employee_details: DF.Table[VehicleRequestEmployee]
		employee_name: DF.ReadOnly | None
		from_date: DF.Datetime
		grade: DF.ReadOnly | None
		items: DF.Table[VehicleRequestItem]
		kilometer_reading: DF.Data | None
		mode_of_travel: DF.Literal["Office Car", "Private Vehicle", "Public Transport"]
		parent_cost_center: DF.Data | None
		place: DF.Data
		posting_date: DF.Date | None
		previous_km: DF.Data | None
		purpose: DF.SmallText
		reason_for_extension: DF.SmallText | None
		rejection_reason: DF.SmallText | None
		time_of_departure: DF.Datetime | None
		to_date: DF.Datetime
		total_days_and_hours: DF.ReadOnly | None
		vehicle: DF.Link | None
		vehicle_model: DF.Link | None
		vehicle_number: DF.Data | None
		vehicle_type: DF.Link | None
		verifier: DF.Link | None
		verifier_designation: DF.Data | None
		verifier_name: DF.Data | None
		workflow_state: DF.Link | None
	# end: auto-generated types
	def validate(self):
		validate_workflow_states(self)
		notify_workflow_states(self)		
		self.check_duplicate_entry()
		self.calculate_time()
		self.check_date()
		self.fetch_departrure_time()
		if self.kilometer_reading:
			if flt(self.previous_km) > flt(self.kilometer_reading):
				frappe.throw("Kilometer reading must be greater than previous kilometer reading.")
		if self.workflow_state != "Approved":
			notify_workflow_states(self)
			

	def on_submit(self):
		self.notify_employee()

	def on_cancel(self):
		notify_workflow_states(self)
		self.notify_employee()

	def check_duplicate_entry(self):
		data = frappe.db.sql("""
			SELECT vehicle
			FROM `tabVehicle Request`
			WHERE vehicle = '{0}'
			AND docstatus = 1
			AND (from_date BETWEEN '{1}' AND '{2}'
				OR to_date BETWEEN '{1}' AND '{2}')
		""".format(self.vehicle,self.from_date,self.to_date),as_dict=1)
		if data:
			frappe.throw("Vehicle <b>{}</b> is already booked".format(self.vehicle_number))
	
	def calculate_time(self):
		time = time_diff(self.to_date, self.from_date)
		self.total_days_and_hours=time
		return time

	def fetch_departrure_time(self):
		if self.workflow_state == "Waiting Approval":
			get_time = self.from_date
			self.time_of_departure = get_time  

	def  check_date(self):
		if self.from_date > self.to_date:
			frappe.throw("From Date cannot be before than To Date")

	def notify_employee(self):
			driver_email = None
			if self.driver:
				try:
					driver_email = get_employee_email(self.driver)
				except Exception:
					pass

			if not driver_email:
				return

			parent_doc = frappe.get_doc("Vehicle Request", self.name)
			args = parent_doc.as_dict()

			template = frappe.db.get_single_value("HR Settings", "vehicle_request_status_notification_template")
			if not template:
				frappe.msgprint(_("Please set default template for Leave Status Notification in HR Settings."))
				return
			email_template = frappe.get_doc("Email Template", template)
			message = frappe.render_template(email_template.response_, args)

			# Send to driver only
			self.notify(
				{
					"message": message,
					"message_to": driver_email,
					"subject": email_template.subject,
					"notify": "driver",
				}
			)

	def notify(self, args):
		args = frappe._dict(args)
		# args -> message, message_to, subjects
		contact = args.message_to
		if not isinstance(contact, list):
			if not args.notify == "employee":
				contact = frappe.get_doc("User", contact).email or contact

		sender = dict()
		sender["email"] = frappe.get_doc("User", frappe.session.user).email
		sender["full_name"] = get_fullname(sender["email"])

		try:
			frappe.sendmail(
				recipients=contact,
				sender=sender["email"],
				subject=args.subject,
				message=args.message,
			)
			frappe.msgprint(_("Email sent to {0}").format(contact))
		except frappe.OutgoingEmailError:
			pass

@frappe.whitelist()  
def check_form_date_and_to_date(from_date, to_date):
	if from_date > to_date:
		frappe.throw("From Date cannot be before than To Date")
@frappe.whitelist()
def create_logbook(source_name, target_doc=None):
	doclist = get_mapped_doc("Vehicle Request", source_name, {
		"Vehicle Request": {
			"doctype": "Vehicle Logbook"
		},
	}, target_doc)

	return doclist

@frappe.whitelist()
def get_previous_km(vehicle, vehicle_number):
	return frappe.db.sql(""" 
	SELECT 
		vr.kilometer_reading as km
	FROM `tabVehicle Request` vr 
	WHERE vr.vehicle ='{}' and vr.vehicle_number='{}' 
	ORDER BY vr.creation DESC LIMIT 1 """.format(vehicle, vehicle_number),as_dict=1)

@frappe.whitelist()
def create_vr_extension(source_name, target_doc=None):
	doclist = get_mapped_doc("Vehicle Request", source_name, {
		"Vehicle Request": {
			"doctype": "Vechicle Request Extension",
			"field_map": {
				"vehicle_request": "name",
				"from_date":"from_date",
				"to_date":"to_date"
			}
		},
	}, target_doc)

	return doclist

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles: 
		return
	if "ADM User" in user_roles or  "Branch Manager" in user_roles or "Fleet Manager" in user_roles:
		return """(
			exists(select 1
				from `tabEmployee` as e
				where e.branch = `tabVehicle Request`.branch
				and e.user_id = '{user}')
			or
			exists(select 1
				from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
				where e.user_id = '{user}'
				and ab.employee = e.name
				and bi.parent = ab.name
				and bi.branch = `tabVehicle Request`.branch)
		)""".format(user=user)
	else:
		return """(
			exists(select 1
				from `tabEmployee` as e
				where e.name = `tabVehicle Request`.employee
				and e.user_id = '{user}')
		)""".format(user=user)