# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _
from frappe.utils import getdate
import frappe
from frappe.model.document import Document


class EASExtension(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.pms.doctype.eas_extension_details.eas_extension_details import EASExtensionDetails
		from frappe.types import DF

		amended_from: DF.Link | None
		eas_calendar: DF.Link
		eas_extension_details: DF.Table[EASExtensionDetails]
		phase: DF.Literal["", "Target Phase", "Review Phase", "Evaluation Phase"]
		remarks: DF.Text
	# end: auto-generated types
	def validate(self):
		self.set_status()
		#pass
		self.validate_dates()

	def on_submit(self):
		self.update_eas_calendar()
	
	def on_cancel(self):
		self.set_status(update=True)

	def set_status(self, update=False):
		status_map = {0: "Draft", 1: "Submitted", 2: "Cancelled"}
		
		status = status_map.get(self.docstatus, "Unknown")
		
		if update:
			#frappe.throw("hi")
			self.db_set("docstatus", 0)
		else:
			self.status = status

	def update_eas_calendar(self):
		#pass
		doc = frappe.get_doc("EAS Calendar", self.eas_calendar)
		#frappe.throw(self.eas_calendar)
		for tar in doc.items:
			#frappe.throw(str(tar.target_start_date))
			for sour in self.eas_extension_details:
				if tar.eas_group==sour.eas_group:
					#frappe.throw("jjj")
					tar.target_start_date=sour.target_start_date
					tar.target_end_date=sour.target_end_date
					tar.review_start_date=sour.review_end_date
					tar.evaluation_start_date=sour.evaluation_start_date
					tar.db_update() 
					#tar.save()
					break
		frappe.db.commit()
		
	def validate_dates(self):
		#frappe.throw(str(self.eas_calendar))
		eas_calender=frappe.get_doc("EAS Calendar",self.eas_calendar)
		for eas_cal in eas_calender.items:
			for eas_ext in self.eas_extension_details:
				
				if eas_cal.eas_group==eas_ext.eas_group:
					
					if getdate(eas_cal.target_start_date) > getdate(eas_ext.target_start_date):
						frappe.throw(f"{eas_cal.eas_group} The Extension setup  target  date should be grater then calendar set up target")
								
														
					if eas_ext.target_start_date > eas_ext.target_end_date:
						frappe.throw(_("Target start date can not be greater than target end date"))
						
					if eas_ext.review_start_date < eas_ext.target_end_date:
						frappe.throw(_("Review start date can not be greater than target end date"))
						
					if eas_ext.review_start_date > eas_ext.review_end_date:
						frappe.throw(_("Review start date can not be greater than review end date"))
						
					if eas_ext.evaluation_start_date < eas_ext.review_end_date:
						frappe.throw(_("Evaluation start date can not be greater than review end date"))
						
					if eas_ext.evaluation_start_date > eas_ext.evaluation_end_date:
						frappe.throw(_("Evaluation start date can not be greater than evaluation end date"))

					if eas_ext.appeal_start_date < eas_ext.evaluation_end_date:
						frappe.throw(_("Evaluation start date can not be greater than review end date"))
						
					if eas_ext.appeal_start_date > eas_ext.appeal_end_date:
						frappe.throw(_("Evaluation start date can not be greater than evaluation end date")) 

					break