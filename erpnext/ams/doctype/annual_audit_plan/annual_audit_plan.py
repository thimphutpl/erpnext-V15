# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AnnualAuditPlan(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.ams.doctype.aap_q1_item.aap_q1_item import AAPQ1Item
		from erpnext.ams.doctype.aap_q2_item.aap_q2_item import AAPQ2Item
		from erpnext.ams.doctype.aap_q3_item.aap_q3_item import AAPQ3Item
		from erpnext.ams.doctype.aap_q4_item.aap_q4_item import AAPQ4Item
		from frappe.types import DF

		aap_q1_plan: DF.Table[AAPQ1Item]
		aap_q2_plan: DF.Table[AAPQ2Item]
		aap_q3_plan: DF.Table[AAPQ3Item]
		aap_q4_plan: DF.Table[AAPQ4Item]
		amended_from: DF.Link | None
		fiscal_year: DF.Link
		phase: DF.Literal["", "Quarter 1", "Quarter 2", "Quarter 3", "Quarter 4"]
		q1_end_date: DF.Date
		q1_start_date: DF.Date
		q2_end_date: DF.Date
		q2_start_date: DF.Date
		q3_end_date: DF.Date
		q3_start_date: DF.Date
		q4_end_date: DF.Date
		q4_start_date: DF.Date
		remarks: DF.Data | None
	# end: auto-generated types
	def validate(self):
		self.validate_dates()
	 
	def validate_dates(self):
		if self.q1_start_date > self.q1_end_date:
			frappe.throw(_("Quarter 1 start date can not be greater than Quarter 1 end date"))

		if self.q2_start_date > self.q2_end_date:
			frappe.throw(_("Quarter 2 start date can not be greater than Quarter 2 end date"))

		if self.q3_start_date > self.q3_end_date:
			frappe.throw(_("Quarter 3 start date can not be greater than Quarter 3 end date"))

		if self.q4_start_date > self.q4_end_date:
			frappe.throw(_("Quarter 4 start date can not be greater than Quarter 4 end date"))
