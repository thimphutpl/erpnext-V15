# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FinancialInstitution(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.financial_institution_item.financial_institution_item import FinancialInstitutionItem
		from frappe.types import DF

		account_bank_name: DF.Link | None
		account_holder_name: DF.Data | None
		account_no: DF.Data | None
		bank_account_type: DF.Link | None
		bank_branch: DF.Link | None
		bank_code: DF.Data | None
		bank_name: DF.Data
		bank_status: DF.Data | None
		employee_loan_payment_in_single_account: DF.Check
		enabled: DF.Check
		items: DF.Table[FinancialInstitutionItem]
		short_form: DF.Data
	# end: auto-generated types
	
	def onload(self):
		self.load_branches()

	def validate(self):
		self.validate_mandatory()
		self.sync_branches()
		self.items = []

	def validate_mandatory(self):
		if not self.bank_name:
			frappe.throw(_("Bank Name is mandatory"))

	def get_branches(self):
		return frappe.get_all("Financial Institution Branch", "*", {"financial_institution": self.name}, order_by="branch_name")

	def load_branches(self):
		self.items = []
		for branch in self.get_branches():
			self.append("items",{
				"branch_name": branch.branch_name,
				"financial_system_code": branch.financial_system_code,
				"financial_institution_branch": branch.name
			})

	def sync_branches(self):
		for item in self.items:
			if item.financial_institution_branch:
				branch = frappe.get_doc("Financial Institution Branch", item.financial_institution_branch)
			else:
				branch = frappe.new_doc("Financial Institution Branch")

			branch.update({
				"financial_institution": self.name,
				"branch_name": str(item.branch_name).strip(),
				"financial_system_code": str(item.financial_system_code).strip()
			})
			branch.save(ignore_permissions=True)

