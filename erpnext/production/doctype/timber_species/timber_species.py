# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class TimberSpecies(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		species: DF.Data
		timber_class: DF.Link
		timber_type: DF.Literal["Conifer", "Broadleaf"]
	# end: auto-generated types
	def autoname(self):
		self.species = self.species.strip()
		self.check_duplicate(self.species.lower())

	def validate(self):
		pass

	def check_duplicate(self, species):
		for a in frappe.db.sql("select name from `tabTimber Species` where LOWER(name) = %s", species, as_dict=1):
			frappe.throw("Species {0} already created".format(a.name))


