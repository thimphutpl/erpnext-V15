# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
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
		from erpnext.pms.doctype.work_competency_item.work_competency_item import WorkCompetencyItem
		from frappe.types import DF

		apply_to_all: DF.Check
		competency: DF.Data
		description: DF.SmallText | None
		disabled: DF.Check
		employee_group_item: DF.Table[WorkCompetencyItem]
		weightage: DF.Float
	# end: auto-generated types
	def autoname(self):
		self.name = make_autoname("WCOMP.#.-.{}".format(str(self.naming_series)))
