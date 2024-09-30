# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from frappe.utils import nowdate

class Scholarship(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.gift__management.doctype.family_detail_table.family_detail_table import FamilyDetailTable
		from erpnext.gift__management.doctype.student_achievement_table.student_achievement_table import StudentAchievementTable
		from frappe.types import DF

		accommodation_charge: DF.Data | None
		batch: DF.Data
		cid_number: DF.Data
		college: DF.Data
		college_name: DF.Data | None
		completed_datexii: DF.Date | None
		contact_number: DF.Data
		country: DF.Data
		course: DF.Link
		cumulative_gpa: DF.Data | None
		date_of_birth: DF.Date
		disbursement: DF.SmallText | None
		dzongkhag: DF.Data | None
		email_address: DF.Data
		end_date: DF.Date
		english: DF.Data | None
		family_details: DF.Table[FamilyDetailTable]
		gewog: DF.Data | None
		highschool: DF.Data | None
		middle_school: DF.Data | None
		name1: DF.Data
		percentage: DF.Data | None
		percentagex: DF.Data | None
		permanent_address: DF.Data
		present_address: DF.Data | None
		profile_picture: DF.AttachImage | None
		rankxii: DF.Data | None
		royal_command: DF.Text | None
		start_date: DF.Date
		status: DF.Literal["On-Going", "Completed"]
		stream: DF.Data | None
		streamx: DF.Data | None
		student_achievements: DF.Table[StudentAchievementTable]
		student_id: DF.Data | None
		tuition_fee: DF.Data | None
		village: DF.Data | None
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

