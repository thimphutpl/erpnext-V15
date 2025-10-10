# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from erpnext.custom_workflow import notify_workflow_states, validate_workflow_states


class ManagingforExcellence(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.max.doctype.max_competency_item.max_competency_item import MaxCompetencyItem
		from erpnext.max.doctype.max_item.max_item import MAXitem
		from frappe.types import DF

		amended_from: DF.Link | None
		appraisal_period: DF.Link
		approver: DF.Link | None
		approver_designation: DF.Data | None
		approver_email: DF.Link | None
		approver_name: DF.Data | None
		company: DF.Link
		competency_item: DF.Table[MaxCompetencyItem]
		designation: DF.Link | None
		employee: DF.Link
		employee_name: DF.Data | None
		items: DF.Table[MAXitem]
		overall_score: DF.Literal["", "Outstanding", "Very Good", "Good", "Partially Meeting Expectations"]
		pms_group: DF.Link
		required_to_set_target: DF.Check
	# end: auto-generated types
	def validate(self):
		validate_workflow_states(self)
		self.check_duplicate()
		self.add_approver_user()
		if not self.workflow_state=='Planning':
			if not self.items:
				frappe.throw("Target Items in Section B are Mandatory")

	def add_approver_user(self):
		if self.approver:
			approver_user = frappe.db.get_value("Employee",{"name":self.approver},"user_id")
			if approver_user:
				self.approver_email = approver_user

	def check_duplicate(self):
		if frappe.db.exists(
			"Managing for Excellence",
			{
				"employee": self.employee,
				"name": ["!=", self.name],
				"appraisal_period":self.appraisal_period  # exclude current record
			}
		):
			frappe.throw("Already exists for this employee")

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)
	

	# reviewers  = frappe.db.sql("SELECT user_id FROM `tabeNote Reviewer")
	
	if user == "Administrator":
		return
	# if "HR User" in user_roles or "HR Manager" in user_roles:
	#     return
	# return """(
	# 	`tabManaging for Excellence`.owner = '{user}' 
		
	# 	or

	# 	exists(select 1
	# 		from `tabEmployee` e, `tabNote Copy` nc
	# 		where e.user_id = '{user}' and '{user}' = nc.employee and nc.parent = `tabeNote`.name)
   	# 	)
	# 	""".format(user=user)
	return """(
        `tabManaging for Excellence`.owner = '{user}'

		or 

		`tabManaging for Excellence`.approver_email = '{user}'
       
        
    )""".format(user=user)

@frappe.whitelist()
def get_max_competency(name, pms_group):
	competency = frappe.db.sql('''
        SELECT competency_item, description
        FROM `tabCompetency Master Item`
        WHERE parent = %s order by serial_number asc
    ''', (pms_group,), as_dict=True)

	return competency

@frappe.whitelist()
def get_target_fields(pms_group):
	pms_group = frappe.db.sql('''
        select required_activity, 
		required_area, 
		required_baselined, 
		required_key_result_areas 
		from `tabPMS Group` where name= %s
    ''', (pms_group,), as_dict=True)

	return pms_group



