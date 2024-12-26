# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectOvertimeTool(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		branch: DF.Link | None
		cost_center: DF.Link | None
		date: DF.Date | None
		employee_type: DF.Literal["", "Muster Roll Employee", "Open Air Prisoner", "Operator"]
		number_of_hours: DF.Float
		project: DF.Link | None
		purpose: DF.SmallText | None
	# end: auto-generated types
	pass
