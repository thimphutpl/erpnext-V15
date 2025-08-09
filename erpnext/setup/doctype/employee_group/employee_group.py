# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from frappe.model.document import Document


class EmployeeGroup(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.setup.doctype.employee_group_table.employee_group_table import EmployeeGroupTable
		from frappe.types import DF
		from hrms.hr.doctype.employee_group_item.employee_group_item import EmployeeGroupItem

		employee_group_name: DF.Data
		employee_list: DF.Table[EmployeeGroupTable]
		employee_pf: DF.Percent
		employer_pf: DF.Percent
		encashment_frequency: DF.Int
		encashment_lapse: DF.Float
		encashment_min: DF.Float
		health_contribution: DF.Percent
		increment_prorated: DF.Check
		items: DF.Table[EmployeeGroupItem]
		leave_encashment_amount: DF.Currency
		leave_encashment_months: DF.Float
		leave_encashment_type: DF.Literal["", "Flat Amount", "Basic Pay", "Gross Pay"]
		limit_multiplier: DF.Float
		loan_type: DF.Literal["Gross Pay"]
		max_encashment_days: DF.Float
		maximum_number_of_months_allowed: DF.Data | None
		min_encashment_days: DF.Float
		minimum_months: DF.Float
		minimum_service_period: DF.Int
		no_of_installment_for_salary: DF.Literal["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
		noof_installment: DF.Literal["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60"]
		retirement_age: DF.Int
		salary_advance_limit: DF.Data | None
		salary_advance_max_months: DF.Float
		salary_advance_type: DF.Literal["", "Flat Amount", "Basic Pay", "Net Pay", "Gross Pay"]
	# end: auto-generated types

	pass
