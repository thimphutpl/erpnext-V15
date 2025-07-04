# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class EASCalendar(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.pms.doctype.eas__group_details.eas__group_details import EASGroupDetails
		from frappe.types import DF

		amended_from: DF.Link | None
		appeal_end_date: DF.Date | None
		appeal_start_date: DF.Date | None
		eas_group: DF.Link | None
		evaluation_end_date: DF.Date | None
		evaluation_start_date: DF.Date | None
		fiscal_year: DF.Link
		items: DF.Table[EASGroupDetails]
		phase: DF.Literal["", "Target Phase", "Review Phase", "Evaluation Phase"]
		remarks: DF.Data | None
		review_end_date: DF.Date | None
		review_start_date: DF.Date | None
		target_end_date: DF.Date | None
		target_start_date: DF.Date | None
	# end: auto-generated types
	def validate(self):
		# for gr in self.items:
		# 	frappe.throw(gr.eas_group)
				  
		self.validate_dates()
			
	def validate_dates(self):
		for gr in self.items:
			#frappe.throw(gr.eas_group)
			if gr.eas_group=="Group I":
				if gr.target_start_date > gr.target_end_date:
					frappe.throw(_("Target start date can not be greater than target end date"))

				if gr.review_start_date < gr.target_end_date:
					frappe.throw(_("Review start date can not be greater than target end date"))

				if gr.review_start_date > gr.review_end_date:
					frappe.throw(_("Review start date can not be greater than review end date"))

				if gr.evaluation_start_date < gr.review_end_date:
					frappe.throw(_("Evaluation start date can not be greater than review end date"))   

				if gr.evaluation_start_date > gr.evaluation_end_date:
					frappe.throw(_("Evaluation start date can not be greater than evaluation end date")) 


		pass


@frappe.whitelist()
def create_eas_extension(source_name, target_doc=None):
	#frappe.throw(source_name)
	doclist = get_mapped_doc("EAS Calendar", source_name, {
		"EAS Calendar": {
			"doctype": "EAS Extension",
			"field_map": {
                "eas_calendar": "name"
            },
		 "EAS  Group Details":{
			 "doctype":"EAS Extension Details"

		 }
		},
	}, target_doc)

	return doclist