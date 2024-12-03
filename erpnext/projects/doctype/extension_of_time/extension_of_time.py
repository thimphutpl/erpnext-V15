# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, flt, get_datetime, get_time, get_url, nowtime, today, getdate, date_diff


class ExtensionofTime(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		eot_in_days: DF.Int
		expected_end_date: DF.Date | None
		expected_start_date: DF.Date | None
		extended_end_date: DF.Date
		extension_order: DF.Attach | None
		projects: DF.Link
		reason_for_extension: DF.TextEditor
		title: DF.Data
	# end: auto-generated types
	
	def validate():
		if not self.eot_in_days:
			self.eot_in_days = date_diff(self.extended_end_date, self.expected_end_date)
		
	def on_submit():
		self.update_project()

	def update_project(self):
		doc = frappe.get_doc("Project", self.project)
		doc.db_set('revised_completion_date', self.extended_end_date, update_modified=False)
		doc.db_set('dlp_start_date', add_days(doc.dlp_start_date, self.eot_in_days), update_modified=False)
		doc.db_set('dlp_end_date', add_days(doc.dlp_end_date, self.eot_in_days), update_modified=False)
