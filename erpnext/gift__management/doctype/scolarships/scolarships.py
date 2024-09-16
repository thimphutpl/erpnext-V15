# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class Scolarships(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		batch: DF.Data
		cid_number: DF.Data
		college: DF.Data
		contact_number: DF.Data
		country: DF.Data
		course: DF.Literal["Bachelor of Arts in English", "Bachelor of Arts in History", "BSc in Sustainable Development", "BSc in Environment & Climate Studies", "BSc in Animal Science", "BSc in Forestry", "BSc in Food Science and Technology", "BSc in Organic Agriculture", "BSc in Agriculture", "Master of Science in Natural Resources Management", "Masters in Development Practice", "BE in Civil Engineering", "BE in Information Technology", "BE in Electronics & Communications Engineering", "Bachelor of Architecture", "BE in Engineering Geology", "BE in Instrumentation & Control Engineering", "BE in Electrical Engineering", "ME in Renewable Energy", "Bachelor of Business Administration (BBA)", "MBA", "Bachelor of Commerce", "BA in Bhutanese & Himalayan Studies", "BA in Language & Literature", "Diploma in Language & Literature", "Diploma in Materials and Procurement Management", "Bachelor of Engineering in Surveying & Geoinformatics", "Diploma in Computer System & Network", "Diploma in Civil Engineering", "Diploma in Surveying", "Bachelor of Engineering in Mechanical Engineering", "Bachelor of Engineering in Power Engineering", "Diploma in Mechanical Engineering", "BEd (Primary)", "B.Ed (Primary)", "BEd (Dzongkha)", "Diploma in Early Childhood, Care\u00a0 and Development", "Diploma in Early Childhood, Care\u00a0 and Development", "MEd in Dzongkha Education", "Pg Diploma in Education (Dzongkha)", "Pg Diploma in Education (Dzongkha)", "Bachelors in Education Secondary", "Bachelor of Arts in Social Work", "Master of Education in English", "Postgraudate Diploma in Contemplative Counselling Psychology", "Master of Education in Science (Biology/Chemistry/Physics) and Mathematics", "M.Ed in Geography", "Postgraduate Diploma in Education", "B.A Political Science and Sociology", "B.A (Honours) Political Science and Sociology", "BA Population and Development Studies", "B.Sc. (Honours) Population and Development Studies/td>", "B.Sc.Life Science", "B.Sc. (Honours) Botany", "B.Sc. (Honours) Zoology", "Bachelor of Science in Chemistry", "Bachelor of Science (Honours) in Chemistry", "BSc in Geography &\u00a0BSc Honours in Geography", "B.A Dzongkha and English", "B.A. (Honours) English", "B.A. (Honours) Dzongkha", "Bachelor of Science in Physics", "Bachelor of Science (Honours) in Physics", "Bachelor of Arts in Economics & Bachelor of Arts Honours in Economics", "B.Sc.Mathematics", "B.Sc. (Honours) Mathematics", "B.Sc.Environmental Science", "B.A. (Honours) Environmental Science", "Bachelor in Computer Application", "Bachelor of Science in Computer Science", "Bachelor of Science in Information Technology"]
		email_address: DF.Data
		end_date: DF.Datetime
		name1: DF.Data
		permanent_address: DF.Data
		start_date: DF.Datetime
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
