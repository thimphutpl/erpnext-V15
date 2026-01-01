# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ContractFocalTransfer(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		contract: DF.Link | None
		end_date: DF.Date | None
		focal_person: DF.Link | None
		focal_person_name: DF.Data | None
		new_focal_person: DF.Link | None
		new_focal_person_name: DF.Data | None
		posting_date: DF.Date | None
		start_date: DF.Date | None
	# end: auto-generated types
	# pass

	def validate(self):
		if not self.contract:
			frappe.throw("Contract is required.")

		if not self.new_focal_person:
			frappe.throw("New Focal Person is required.")

		if self.new_focal_person == self.focal_person:
			frappe.throw("New Focal Person cannot be the same as current Focal Person.")

	def on_submit(self):
		self.apply_transfer()

	def apply_transfer(self):
		frappe.db.set_value(
			"Contract Details",
			self.contract,
			{
				"focal_person": self.new_focal_person,
				"focal_person_name": self.new_focal_person_name,
			},
			update_modified=True
		)