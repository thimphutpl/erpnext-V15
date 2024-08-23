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
		asset_issue_details: DF.Link | None
		branch: DF.Link | None
		capacity: DF.Data | None
		chasis_number: DF.Data | None
		company: DF.Link | None
		consultant: DF.Check
		consultant_name: DF.Data | None
		creation_date: DF.Date
		current_operator: DF.Data | None
		dzongkhag: DF.Link | None
		emission_standard: DF.Data | None
		enabled: DF.Check
		engine_number: DF.Data | None
		equipment_category: DF.Link
		equipment_description: DF.SmallText | None
		equipment_history: DF.Table[EquipmentHistory]
		equipment_model: DF.Link
		equipment_name: DF.Data | None
		equipment_operator: DF.Table[EquipmentOperator]
		equipment_type: DF.Link
		fuel_type: DF.Link
		fuelbook: DF.Link | None
		gewog: DF.Link | None
		hired_equipment: DF.Check
		initial_km_reading: DF.Float
		is_container: DF.Check
		make: DF.Data | None
		model_items: DF.Table[EquipmentModelHistory]
		purchase_date: DF.Date | None
		purchase_rate: DF.Currency
		purchase_receipt: DF.Link | None
		rate: DF.Currency
		reading_uom: DF.Data | None
		registeration_number: DF.Data
		status: DF.Literal["", "Running", "Maintenance"]
		supplier: DF.Link | None
		village: DF.Link | None
		wheeler: DF.Literal["", "26", "10", "6", "4", "2"]
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