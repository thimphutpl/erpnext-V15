# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate, cint

class Equipment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.equipment_history.equipment_history import EquipmentHistory
		from erpnext.fleet_management.doctype.equipment_model_history.equipment_model_history import EquipmentModelHistory
		from erpnext.fleet_management.doctype.equipment_operator.equipment_operator import EquipmentOperator
		from frappe.types import DF

		asset_code: DF.Link | None
		bluebook_date: DF.Date | None
		branch: DF.Link
		chasis_number: DF.Data | None
		current_hr_reading: DF.ReadOnly | None
		current_km_reading: DF.ReadOnly | None
		current_operator: DF.Data | None
		details: DF.SmallText | None
		disabled_date: DF.Date | None
		dzongkhag: DF.Link | None
		engine_number: DF.Data | None
		equipment_category: DF.Link
		equipment_history: DF.Table[EquipmentHistory]
		equipment_model: DF.Link
		equipment_operator: DF.Table[EquipmentOperator]
		equipment_type: DF.Link
		fuelbook: DF.Link | None
		gewog: DF.Link | None
		hsd_type: DF.Link | None
		is_disabled: DF.Check
		model_items: DF.Table[EquipmentModelHistory]
		not_cdcl: DF.Check
		registeration_number: DF.Data | None
		supplier: DF.Link | None
		village: DF.Link | None
	# end: auto-generated types
	def validate(self):
		self.update_equipment_hiring_form()
		# self.validate_asset_fuelbook()
	
	# def validate_asset_fuelbook(self):
	# 	if self.asset_code:
	def update_equipment_hiring_form(self):
		if self.supplier != frappe.db.get_value(self.doctype, self.name,"supplier") and cint(self.hired_equipment) == 1:
			frappe.db.sql("update `tabEquipment Hiring Form` set supplier = '{}' where equipment = '{}'".format(self.supplier, self.name))
		
	@frappe.whitelist()
	def create_equipment_history(self, branch, on_date, ref_doc, purpose):
		from_date = on_date
		if purpose == "Cancel":
			to_remove = []
			for a in self.equipment_history:
				if a.reference_document == ref_doc:
					to_remove.append(a)

			[self.remove(d) for d in to_remove]
			self.set_to_date()
			return

		if not self.equipment_history:
			self.append("equipment_history", {
				"branch": self.branch,
				"from_date": from_date,
				"supplier": self.supplier if self.hired_equipment else '',
				"reference_document": ref_doc,
				"bank_name": self.bank_name,
				"account_number": self.account_number,
				"ifs_code": self.ifs_code
			})
		else:
			#doc = frappe.get_doc(self.doctype,self.name)
			ln = len(self.equipment_history)-1
			if ln < 0:
				self.append("equipment_history", {
					"branch": self.branch,
					"from_date": from_date,
					"supplier": self.supplier if self.hired_equipment else '',
					"reference_document": ref_doc,
					"bank_name": self.bank_name,
					"account_number": self.account_number,
					"ifs_code": self.ifs_code
				})
			elif self.branch != self.equipment_history[ln].branch or self.supplier != self.equipment_history[ln].supplier:
				self.append("equipment_history", {
					"branch": self.branch,
					"from_date": from_date,
					"supplier": self.supplier if self.hired_equipment else '',
					"reference_document": ref_doc,
					"bank_name": self.bank_name,
					"account_number": self.account_number,
					"ifs_code": self.ifs_code
				})
			self.set_to_date()

	def set_to_date(self):
		if len(self.equipment_history) > 1:
			for a in range(len(self.equipment_history)-1):
				self.equipment_history[a].to_date = frappe.utils.data.add_days(
					getdate(self.equipment_history[a + 1].from_date), -1)
		else:
			self.equipment_history[0].to_date = None

	def set_name(self):
		for a in self.operators:
			if a.employee_type == "Employee":
				a.operator_name = frappe.db.get_value("Employee", a.operator, "employee_name")
			if a.employee_type == "Muster Roll Employee":
				a.operator_name = frappe.db.get_value("Muster Roll Employee", a.operator, "person_name")

	def validate_asset(self):
		if self.asset_code:
			equipments = frappe.db.sql("select name from tabEquipment where asset_code = %s and name != %s", (self.asset_code, self.name), as_dict=True)
			if equipments:
				frappe.throw("The Asset is already linked to another equipment")


@frappe.whitelist()
def get_yards(equipment):
	t, m = frappe.db.get_value("Equipment", equipment, ['equipment_type', 'equipment_model'])
	data = frappe.db.sql("select lph, kph from `tabHire Charge Parameter` where equipment_type = %s and equipment_model = %s", (t, m), as_dict=True)
	if not data:
		frappe.throw("Setup yardstick for " + str(m))
	return data

@frappe.whitelist()
def get_equipments(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("select a.equipment as name from `tabHiring Approval Details` a where docstatus = 1 and a.parent = \'"+ str(filters.get("ehf_name")) +"\'")

def sync_branch_asset():
	objs = frappe.db.sql("select e.name, a.branch from tabEquipment e, tabAsset a where e.asset_code = a.name and e.branch != a.branch", as_dict=True)
	for a in objs:
		frappe.db.sql("update tabEquipment set branch = %s where name = %s", (a.branch, a.name))

