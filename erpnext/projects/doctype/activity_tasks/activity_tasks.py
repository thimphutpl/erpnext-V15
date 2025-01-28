# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ActivityTasks(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		activity: DF.Data | None
		description: DF.TextEditor | None
		end_date: DF.Date
		grp_exp_end_date: DF.Date | None
		grp_exp_start_date: DF.Date | None
		grp_work_quantity: DF.Percent
		grp_work_quantity_complete: DF.Percent
		is_group: DF.Check
		parent: DF.Data
		parent_task: DF.Link | None
		parentfield: DF.Data
		parenttype: DF.Data
		start_date: DF.Date
		status: DF.Literal["Open", "Working", "Pending Review", "Closed", "Cancelled"]
		target_quantity: DF.Float
		target_quantity_complete: DF.Float
		target_uom: DF.Link | None
		task: DF.Data
		task_achievement_percent: DF.Data | None
		task_duration: DF.Data | None
		task_id: DF.Link | None
		task_weightage: DF.Data | None
		work_quantity: DF.Float
		work_quantity_complete: DF.Float
	# end: auto-generated types
	pass
