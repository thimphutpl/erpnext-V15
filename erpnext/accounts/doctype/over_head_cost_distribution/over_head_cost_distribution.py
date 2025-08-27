# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class OverHeadCostDistribution(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.over_head_cost_item.over_head_cost_item import OverHeadCostItem
		from frappe.types import DF

		account: DF.Link
		amended_from: DF.Link | None
		distribution_type: DF.Literal["", "Cost Center to Cost Center", "Cost Center to Project"]
		from_date: DF.Date
		over_head_cost_item: DF.Table[OverHeadCostItem]
		posting_date: DF.Date
		project_count: DF.Data | None
		remarks: DF.Text | None
		source_branch: DF.Link
		source_cost_center: DF.Link
		source_total_amount: DF.Currency
		sum_cost_driver: DF.Data | None
		target_branch: DF.Link | None
		target_cost_center: DF.Link | None
		to_date: DF.Date
	# end: auto-generated types
	def validate(self):
		pass
	@frappe.whitelist()
	def get_over_head_cost(self):
		if not self.from_date or not self.to_date:
			frappe.throw("From Date and To Date are mandatory to fetch Over Head Cost")
		if not self.source_cost_center:
			frappe.throw("Source Cost Center is mandatory to fetch Over Head Cost")
		if not self.account:
			frappe.throw("Account is mandatory to fetch Over Head Cost")

		over_head = frappe.db.sql("""
			SELECT 
				SUM(gl.credit) AS total_credit, 
				SUM(gl.debit) AS total_debit
			FROM `tabGL Entry` gl
			INNER JOIN `tabAccount` ac ON gl.account = ac.name
			WHERE gl.is_cancelled = 0
			AND gl.cost_center = %s
			AND gl.posting_date BETWEEN %s AND %s
			AND ac.root_type = 'Expense'
			And gl.account = %s
			AND (gl.project IS NULL OR gl.project = '')
		""", (self.source_cost_center, self.from_date, self.to_date, self.account), as_dict=True)

		if over_head:
			for row in over_head:
				amount= flt(row.total_debit) - flt(row.total_credit)
				if amount > 0:
					return amount
				else:
					frappe.throw("No Over Head Cost found for the selected criteria")
		else:
			frappe.throw("No Over Head Cost found for the selected criteria")
	
	@frappe.whitelist()
	def get_project(self):
		if not self.from_date or not self.to_date:
			frappe.throw("From Date and To Date are mandatory to Project")
		if not self.source_cost_center:
			frappe.throw("Source Cost Center is mandatory to fetch Project")
		if not self.account:
			frappe.throw("Account is mandatory to fetch Project")

		project = frappe.db.sql("""
			SELECT 
				name, 
				branch,
				cost_center,
				physical_progress_weightage
			FROM `tabProject`
			WHERE physical_progress_weightage != 0
			AND branch = %s
			AND cost_center = %s
		""", (self.source_branch, self.source_cost_center), as_dict=True)
		# frappe.throw(str(project))
		if project:
			doc = frappe.get_doc("Over Head Cost Distribution", self.name)
			for raw in project:
				doc.append("over_head_cost_item",{
				"target_branch": raw.branch,
				"target_cost_center": raw.cost_center,
				"project": raw.name,
				"cost_driver": raw.physical_progress_weightage
			})
			doc.save(ignore_permissions=True)
			return 1
		else:
			frappe.throw("No Project found for the selected criteria")

