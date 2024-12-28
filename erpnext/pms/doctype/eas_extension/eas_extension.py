# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _
import frappe
from frappe.model.document import Document


class EASExtension(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		eas_calendar: DF.Link
		evaluation_end_date: DF.Date | None
		evaluation_start_date: DF.Date | None
		phase: DF.Literal["", "Target Phase", "Review Phase", "Evaluation Phase"]
		remarks: DF.Text
		review_end_date: DF.Date | None
		review_start_date: DF.Date | None
		target_end_date: DF.Date | None
		target_start_date: DF.Date | None
	# end: auto-generated types
	def validate(self):
		self.validate_dates()

	def on_submit(self):
		self.update_eas_calendar()

	def update_eas_calendar(self):
		doc = frappe.get_doc("EAS Calendar", self.eas_calendar)
		doc.target_start_date = self.target_start_date
		doc.target_end_date = self.target_end_date
		doc.review_start_date = self.review_start_date
		doc.review_end_date = self.review_end_date
		doc.evaluation_start_date = self.evaluation_start_date
		doc.evaluation_end_date = self.evaluation_end_date
		doc.remarks = self.remarks
		doc.save(ignore_permissions=True)
	def validate_dates(self):
		if self.target_start_date > self.target_end_date:
			frappe.throw(_("Target start date can not be greater than target end date"))
			
		if self.review_start_date < self.target_end_date:
			frappe.throw(_("Review start date can not be greater than target end date"))
			
		if self.review_start_date > self.review_end_date:
			frappe.throw(_("Review start date can not be greater than review end date"))
			
		if self.evaluation_start_date < self.review_end_date:
			frappe.throw(_("Evaluation start date can not be greater than review end date"))
			
		if self.evaluation_start_date > self.evaluation_end_date:
			frappe.throw(_("Evaluation start date can not be greater than evaluation end date")) 

