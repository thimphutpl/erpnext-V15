# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class RiskFactor(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF


	# end: auto-generated types
	def validate(self):
		self.calculate_risk_score()

	def calculate_risk_score(self):
		tot = 0
		tot += self.cal_prior_audit_work()
		tot += self.cal_changes()
		tot += self.cal_complexity()
		tot += self.cal_budget()
		tot += self.cal_operating_management()
		tot += self.cal_control_environment()
		tot += self.cal_sensitivity()
		tot += self.cal_staff()

		self.risk_score = tot

	def cal_prior_audit_work(self):	
		if self.prior_audit_work == "&gt;3yrs":
			return 3 
		elif self.prior_audit_work == "1-2yrs":
			return 2
		else:
			return 1
	
	def cal_changes(self):
		if self.changes == "Many": 
			return 3 
		elif self.changes == "Some":
			return 2
		else:
			return 1

	def cal_budget(self):
		if self.budget == "High": 
			return 3 
		elif self.budget == "Medium":
			return 2
		else:
			return 1
	
	def cal_complexity(self):
		if self.complexity == "High": 
			return 3 
		elif self.complexity == "Medium":
			return 2
		else:
			return 1
	
	def cal_operating_management(self):
		if self.operating_management == "Poor": 
			return 3 
		elif self.operating_management == "Satisfactory":
			return 2
		else:
			return 1
	
	def cal_control_environment(self):
		if self.control_environment == "Very Weak": 
			return 3 
		elif self.control_environment == "Weak":
			return 2
		else:
			return 1
	
	def cal_sensitivity(self):
		if self.sensitivity == "Frontline": 
			return 3 
		elif self.sensitivity == "Significant":
			return 2
		else:
			return 1
	
	def cal_staff(self):
		if self.staff == "High": 
			return 3 
		elif self.staff == "Medium":
			return 2
		else:
			return 1
