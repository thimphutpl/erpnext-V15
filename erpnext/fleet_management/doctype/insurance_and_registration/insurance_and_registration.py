# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, money_in_words
from erpnext.accounts.doctype.business_activity.business_activity import get_default_ba
from erpnext.accounts.party import get_party_account

class InsuranceandRegistration(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.bluebook_and_emission.bluebook_and_emission import BluebookandEmission
		from erpnext.fleet_management.doctype.claim_details.claim_details import ClaimDetails
		from erpnext.fleet_management.doctype.insurance_details.insurance_details import InsuranceDetails
		from erpnext.fleet_management.doctype.registration_details.registration_details import RegistrationDetails
		from frappe.types import DF

		amended_from: DF.Link | None
		asset_category: DF.ReadOnly | None
		asset_name: DF.ReadOnly | None
		asset_sub_category: DF.ReadOnly | None
		branch: DF.ReadOnly | None
		chassis_number: DF.ReadOnly | None
		claim_items: DF.Table[ClaimDetails]
		engine_number: DF.ReadOnly | None
		equipment_model: DF.Link | None
		equipment_number: DF.ReadOnly | None
		equipment_type: DF.Link | None
		in_items: DF.Table[InsuranceDetails]
		insurance_for: DF.Literal["", "Equipment", "Asset", "Project"]
		insurance_type: DF.DynamicLink
		model: DF.Data | None
		plot_no: DF.Data | None
		posting_date: DF.Date
		reg_items: DF.Table[RegistrationDetails]
		table_quie: DF.Table[BluebookandEmission]
	# end: auto-generated types
	def validate(self):
		self.validate_insuranced()
		if self.in_items:
			self.posting_date = self.in_items[-1].due_date

	def validate_insuranced(self):
		insured_list = frappe.db.sql("""select name, insurance_type from `tabInsurance and Registration` """, as_dict =1)
		for a in insured_list:
			if self.insurance_type == a.insurance_type:
				if self.name != a.name:
					frappe.throw ("Insurance and Registration transaction of the {0} is already saved in {1} document".format(self.insurance_type, a.name))	

