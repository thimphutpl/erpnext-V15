# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectsAccountsSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		accrued_expense_account: DF.Link | None
		advance_account_internal: DF.Link | None
		advance_account_supplier: DF.Link
		dfg_overtime_account: DF.Link
		dfg_wage_account: DF.Link
		gep_overtime_account: DF.Link
		gep_overtime_accounts: DF.Link | None
		gep_wages_account: DF.Link
		gep_wages_accounts: DF.Link | None
		inventory_account: DF.Link | None
		inventory_accounts: DF.Link | None
		invoice_account_internal: DF.Link | None
		invoice_account_supplier: DF.Link | None
		mr_overtime_account: DF.Link
		mr_wages_account: DF.Link
		oap_gratuity_account: DF.Link
		oap_overtime_account: DF.Link
		oap_wage_account: DF.Link
		operator_allowance_account: DF.Link
		operator_overtime_account: DF.Link
		project_accrued_income_account: DF.Link
		project_accrued_income_accounts: DF.Link | None
		project_advance_account: DF.Link
		project_advance_accounts: DF.Link | None
		project_invoice_account: DF.Link
		project_invoice_accounts: DF.Link | None
		retention_account_receivable: DF.Link | None
	# end: auto-generated types
	pass
