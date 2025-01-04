# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from erpnext.custom_utils import get_branch_cc, get_cc_customer, sendmail
from frappe.utils import flt


class EquipmentRequest(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.equipment_request_item.equipment_request_item import EquipmentRequestItem
		from frappe.types import DF

		amended_form: DF.Link | None
		amended_from: DF.Link | None
		branch: DF.ReadOnly
		cost_center: DF.ReadOnly | None
		ehf: DF.Data | None
		items: DF.Table[EquipmentRequestItem]
		percent_completed: DF.Percent
		purpose: DF.Text | None
		request_date: DF.Date
		requesting_project: DF.Link
		sbranch: DF.Link
	# end: auto-generated types
	def validate(self):
		self.calculate_percent()
		a = frappe.session.user
		# self.check_rejection_msg()
	def calculate_percent(self):
		total_item = len(self.items)
		per_item = flt(flt(100) / flt(total_item), 2)
		for a in self.items:
			a.percent_share = per_item	

	def on_update_after_submit(self):
		# self.check_rejection_msg()
		message = ''
		subject = "Equipment Request Notification"
		recipent = self.owner
		'''qty_check = frappe.db.sql(""" select sum(qty) as r_qty, sum(approved_qty) as a_qty from `tabEquipment Request Item` where parent = '{0}'""".format(self.name), as_dict = True)[0]'''
		if self.approval_status == 'Available':
			message = "The Equipment Request No: '{0}' is Approved".format(self.name)
			
			if self.approval_status == 'Unavailable':
				message = "The Equipment Request No: '{0}' is Rejected '{1}'".format(self.name, self.message)

		if self.approval_status == 'Partially Available':
			msg = ''	
			for i in self.items:
				if not i.approved_qty:
					frappe.throw("Approved Qty Is Mandiatory")
				if i.approved_qty > i.qty:
					frappe.throw(" Approved Qty Cannot Be Greater Than Requested Qty")
				msg1 = "({0}: No. Requested: {1}, No. Approved: {2})".format(i.equipment_type, i.qty, i.approved_qty)
				msg = ','.join([msg1])
			message = "The Equipment Request No: '{0}' is Partially Approved as follows: \n {2}".format(self.name, self.approval_status, msg)
		frappe.msgprint(message)
		sendmail(recipent, subject, message)
	# def check_rejection_msg(self):
	# 	if self.approval_status == 'Unavailable' and self.message == None:
    #                     frappe.throw("Rejection Reason Should Be Mandatory")

@frappe.whitelist()
def make_hire_form(source_name, target_doc=None):
	def update_hire_form(obj, target, source_parent):
		target.private = "CDCL"
		target.cost_center = get_branch_cc(obj.sbranch)
	target.customer = get_cc_customer(target.customer_cost_center)
	target.branch = obj.sbranch

	def update_item(obj, target, source_parent):
		target.from_time = "0:00"
		target.to_time = "0:00"
		target.total_hours = obj.total_hours 
		target.request_reference = obj.name
		target.equipment_request = source_parent.name

	def adjust_last_date(source, target):
		pass
		"""target.items[len(target.items) - 1].dsa_percent = 50 
        target.items[len(target.items) - 1].actual_amount = target.items[len(target.items) - 1].actual_amount / 2
        target.items[len(target.items) - 1].amount = target.items[len(target.items) - 1].amount / 2"""

	doc = get_mapped_doc("Equipment Request", source_name, {
		"Equipment Request": {
			"doctype": "Equipment Hiring Form",
			"field_map": {
				"sbranch": "branch",
				"branch": "customer_branch",
				"cost_center": "customer_cost_center",
			},
			"postprocess": update_hire_form,
			"validation": {"docstatus": ["=", 1]}
		},
	}, target_doc, adjust_last_date)
	return doc 	

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles: 
		return

	return """(
		`tabEquipment Request`.owner = '{user}'
		or
		exists(select 1
			from `tabEmployee` as e
			where e.branch = `tabEquipment Request`.branch
			and e.user_id = '{user}')
		or
		exists(select 1
			from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
			where e.user_id = '{user}'
			and ab.employee = e.name
			and bi.parent = ab.name
			and bi.branch = `tabEquipment Request`.branch)
	)""".format(user=user)
