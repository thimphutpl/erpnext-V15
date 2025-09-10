# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe.model.naming import make_autoname

class WorkCompetency(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.pms.doctype.sub_competency.sub_competency import SubCompetency
		from erpnext.pms.doctype.work_competency_item.work_competency_item import WorkCompetencyItem
		from frappe.types import DF

		apply_to_all: DF.Check
		auto_divide_weightage: DF.Check
		competency: DF.Data
		employee_category_item: DF.Table[WorkCompetencyItem]
		group: DF.Link
		is_parent: DF.Check
		naming_series: DF.Literal["", "Form II", "Form III", "Form IV"]
		sub_competency: DF.Table[SubCompetency]
		weightage: DF.Float
	# end: auto-generated types
	pass
	# def autoname(self):
	# 	self.name = make_autoname("WCOMP.#.-.{}".format(str(self.naming_series)))
