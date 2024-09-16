# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from frappe.utils import nowdate

class Scholarship(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		batch: DF.Data
		cid_number: DF.Data
		college: DF.Data
		contact_number: DF.Data
		country: DF.Data
		course: DF.Link
		email_address: DF.Data
		end_date: DF.Date
		name1: DF.Data
		permanent_address: DF.Data
		start_date: DF.Date
		status: DF.Literal["On-Going", "Completed"]
	# end: auto-generated types

	def before_save(self):
		# Get the current date
		today = nowdate()

		# Check if end_date exists and compare it with today's date
		if self.end_date and self.end_date < today:
			# If the end date has passed, set status to "Completed"
			self.status = "Completed"
		else:
			# If the end date has not passed, set status to "On-Going"
			self.status = "On-Going"

