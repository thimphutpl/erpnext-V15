# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate, get_url, today
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
import datetime
from frappe.model.naming import make_autoname
from erpnext.custom_utils import get_branch_cc
from frappe.model.naming import make_autoname
from datetime import date

class ProjectDefinition(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.projects.doctype.ongoing_project_item.ongoing_project_item import OngoingProjectItem
		from frappe.types import DF

		amended_from: DF.Link | None
		budget_profile: DF.Literal["", "Annually", "Overall"]
		company: DF.Link | None
		cost_center: DF.Link | None
		end_date: DF.Date | None
		fiscal_year: DF.Link | None
		project_code: DF.Data | None
		project_code_prefix: DF.Literal["", "GA-J", "GA-K", "GA-T", "GA-P", "GA-B", "GA"]
		project_manager: DF.Link | None
		project_manager_designation: DF.Link | None
		project_manager_name: DF.Data | None
		project_name: DF.Data
		project_profile: DF.Literal["", "Internal", "External"]
		project_sites: DF.Table[OngoingProjectItem]
		start_date: DF.Date | None
		status: DF.Literal["Created", "Budget Released", "Project Released", "Completed"]
		total_overall_project_cost: DF.Currency
	# end: auto-generated types
	def autoname(self):
		self.name = self.project_code_prefix+"-"+self.project_code+" - GYALSUNG"

	def validate(self):
		self.validate_project_profile()
	
	def before_cancel(self):
		project_list = frappe.db.get_list("Project",filters={"project_definition":self.name,"docstatus":["!=",2]})
		if len(project_list)>0:
			frappe.throw("Project Definition {} is linked with Projects {}".format(self.name,project_list))

	def validate_project_profile(self):
		if self.project_profile == "External" and "Accounts Manager" not in frappe.get_roles(frappe.session.user):
			frappe.throw("Please select project profile as Internal.", title = "Invalid Selection")

# ADDED BY Kinley ON 04-06-2024
@frappe.whitelist()
def make_purchase_requisition(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.material_request_type = "Purchase"
		target.reference_type = "Project Definition"
		target.creation_date = date.today()
		target.abbreviation = "PRJ"
		target.naming_series = "Fixed Assets"
		# target.site = frappe.db.get_value("Project", source.project, "site")

	doc = get_mapped_doc("Project Definition", source_name,	{
		"Project Definition": {
			"doctype": "Material Request",
			"field_map": {
				"name" : "reference_name",
			},
		},
	}, target_doc, set_missing_values)

	return doc

@frappe.whitelist()
def make_project(source_name, target_doc=None):
	def update_date(obj, target, source_parent):
		target.supervisor = None
	def set_missing_values(source, target):
		target.project_name = None
		target.branch = frappe.db.get_value("Branch", {"cost_center": source.cost_center})
	doc = get_mapped_doc("Project Definition", source_name, {
			"Project Definition": {
				"doctype": "Project",
				"field_map": {
					"name": "project_definition",
					"project_profile": "project_type"
				},
				"postprocess": update_date,
				"validation": {"docstatus": ["=", 1]}
			},
		}, target_doc, set_missing_values)
	# project_region = frappe.db.sql("select region from `tabRegion Item` where parent='{}'".format(source_name),as_dict=True)
	# data = get_mapped_doc("Project Definiftion", source_name, {
	# 	"Project Definition":{
	# 		"doctype": "Project",
	# 		"field_map": {
	# 			project_region[0][1]: "region"
	# 		},
	# 		"postprocess": update_date,
	# 		"validation": {"docstatus": ["=", 1]}
	# 	},
	# }, target_doc)
	#frappe.throw("project:{}".format(project_region))
	
	return doc


@frappe.whitelist()
def monthly_settlement(source_name, target_doc=None):
	def update_date(obj, target, source_parent):
		target.supervisor = None
		target.purpose = "Settlement"
	doc = get_mapped_doc("Project Definition", source_name, {
			"Project Definition": {
				"doctype": "Monthly Project Settlement",
				"field_map": {"project_profile": "project_type"},
				"postprocess": update_date,
				"validation": {"docstatus": ["!=", 1]}
			},
		}, target_doc)

	return doc

@frappe.whitelist()
def get_project_cost(project_definition):
	project_names = frappe.db.sql("select site_name as name from `tabOngoing Project Item` where parent='{}'".format(project_definition),as_dict=1)
	for item in project_names:
		total_cost = frappe.db.sql("select total_cost from `tabProject` where name='{}'".format(item.name),as_dict=1)
		if total_cost:
			frappe.db.sql("update `tabOngoing Project Item` set total_cost={} where parent='{}' and site_name='{}'".format(total_cost[0].total_cost, project_definition, item.name))

# Following code added by SHIV on 2021/05/13
def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles or "Projects GM" in user_roles:
		return

	return """(
		exists(select 1
			from `tabEmployee` as e
			where e.branch = `tabProject`.branch
			and e.user_id = '{user}')
		or
		exists(select 1
			from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
			where e.user_id = '{user}'
			and ab.employee = e.name
			and bi.parent = ab.name
			and bi.branch = `tabProject`.branch)
	)""".format(user=user)

