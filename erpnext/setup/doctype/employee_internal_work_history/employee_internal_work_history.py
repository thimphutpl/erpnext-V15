# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from frappe.model.document import Document


class EmployeeInternalWorkHistory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		branch: DF.Link | None
		department: DF.Link | None
		designation: DF.Link | None
		division: DF.Link | None
		from_date: DF.Date | None
		grade: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		promotion_due_date: DF.Date | None
		reference_docname: DF.DynamicLink | None
		reference_doctype: DF.Link | None
		reports_to: DF.Link | None
		section: DF.Link | None
		to_date: DF.Date | None
	# end: auto-generated types

	pass
