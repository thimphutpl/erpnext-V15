# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from frappe.model.document import Document


class EmployeeEducation(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		class_per: DF.Data | None
		country: DF.Link | None
		course_name: DF.Link | None
		from_date: DF.Date | None
		level: DF.Literal["Degree", "Post Graduate", "Under Graduate", "Diploma", "Certificate", "PGD", "Class XII", "Others"]
		maj_opt_subj: DF.Text | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		school_univ: DF.Data | None
		to_date: DF.Date | None
		trade: DF.Link | None
		year_of_passing: DF.Data | None
	# end: auto-generated types

	pass
