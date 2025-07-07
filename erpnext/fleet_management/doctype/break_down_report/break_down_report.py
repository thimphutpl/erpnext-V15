# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, add_years
from frappe.model.mapper import get_mapped_doc
from erpnext.custom_utils import check_future_date

class BreakDownReport(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		client: DF.Data | None
		cost_center: DF.Link
		customer: DF.Link
		customer_branch: DF.ReadOnly | None
		customer_cost_center: DF.ReadOnly | None
		date: DF.Date
		defect: DF.TextEditor
		equipment: DF.Link | None
		equipment_category: DF.Link | None
		equipment_model: DF.Link
		equipment_number: DF.Data | None
		equipment_type: DF.Link | None
		fleet_comment: DF.SmallText | None
		job_cards: DF.Link | None
		owned_by: DF.Literal["", "Own", "Others"]
		private_customer_address: DF.SmallText | None
		private_customer_name: DF.Data | None
		project: DF.ReadOnly | None
		time: DF.Time
		workshop_comment: DF.SmallText | None
	# end: auto-generated types

	def validate(self):
		check_future_date(self.date)
		self.validate_equipment()

	def on_submit(self):
		self.assign_reservation()
		self.post_equipment_status_entry()

	def on_cancel(self):
		self.ignore_linked_doctypes = (
			"GL Entry",
			"Job Cards",
		)
		equipment_status_entry = frappe.db.sql(""" select name from `tabEquipment Status Entry` where ehf_name = %s and docstatus = 1""", self.name, as_dict=True)
		for raw in equipment_status_entry:
			tmp_doc = frappe.get_doc("Equipment Status Entry", raw.name)
			if tmp_doc.docstatus == 1:
				tmp_doc.cancel()
		# Uncomment to auto-cancel linked Job Card if needed
		# if self.job_cards:
		# 	job_card = frappe.get_doc("Job Cards", self.job_cards)
		# 	if job_card.docstatus == 1:
		# 		job_card.cancel()
	def validate_equipment(self):
		frappe.logger().info(f"Equipment: {self.equipment}, Branch: {self.branch}, Customer Branch: {self.customer_branch}")
		if self.owned_by in ['CDCL', 'Own']:
			eb = frappe.db.get_value("Equipment", self.equipment, "branch")
			if self.owned_by == "Own" and self.branch != eb:
				frappe.throw(f"Equipment <b>{self.equipment}</b> doesn't belong to your branch")
			if self.owned_by == "CDCL" and self.customer_branch != eb:
				frappe.throw(f"Equipment <b>{self.equipment}</b> doesn't belong to <b>{self.customer_branch}</b>")
			if self.owned_by == "CDCL" and self.cost_center == self.customer_cost_center:
				frappe.throw("Equipment from your branch should be 'Own' and not 'CDCL'")
		else:
			self.equipment = None

	def assign_reservation(self):
		if self.owned_by in ['CDCL', 'Own']:
			doc = frappe.new_doc("Equipment Reservation Entry")
			doc.flags.ignore_permissions = True
			doc.equipment = self.equipment
			doc.reason = "Maintenance"
			doc.ehf_name = self.name
			doc.hours = 100
			doc.place = self.branch
			doc.from_date = self.date
			doc.from_time = self.time
			doc.to_date = add_years(self.date, 1)
			doc.submit()

	def post_equipment_status_entry(self):
		if self.owned_by in ['CDCL', 'Own']:
			ent = frappe.new_doc("Equipment Status Entry")
			ent.flags.ignore_permissions = True
			ent.equipment = self.equipment
			ent.reason = "Maintenance"
			ent.ehf_name = self.name
			ent.hours = 100
			ent.place = self.branch
			ent.from_date = self.date
			ent.from_time = self.time
			ent.to_date = add_years(self.date, 1)
			ent.submit()

@frappe.whitelist()
def make_job_cards(source_name, target_doc=None):
	def update_date(obj, target, source_parent):
		target.posting_date = nowdate()

	doc = get_mapped_doc("Break Down Report", source_name, {
		"Break Down Report": {
			"doctype": "Job Cards",
			"field_map": {
				"name": "Job_Cards",
				"date": "break_down_report_date"
			},
			"postprocess": update_date,
			"validation": {
				"docstatus": ["=", 1],
				"job_cards": ["is", None]
			}
		}
	}, target_doc)

	return doc
