# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class UtilityServices(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.epayment.doctype.utility_services_item.utility_services_item import UtilityServicesItem
		from frappe.types import DF

		bank_account: DF.Data
		branch: DF.Link
		cost_center: DF.Link
		expense_account: DF.Link
		item: DF.Table[UtilityServicesItem]
	# end: auto-generated types
	def validate(self):
		self.validate_duplicate()
	
	def validate_duplicate(self):
		result = frappe.db.sql("""select name
								from `tabUtility Services`
								where branch = '{}'
								and name != '{}'
							""".format(self.branch, self.name))
		if result:
			frappe.throw("Utility services for {} branch already exists.".format(self.branch))
		
		for a in self.item:
			result1 = frappe.db.sql("""select name
								from `tabUtility Services Item`
								where consumer_code = '{}'
								and utility_service_type = '{}'
								and parent != '{}'
							""".format(a.consumer_code, a.utility_service_type, self.name))
			if result1:
				frappe.throw("Record already exist with customer code {} and Utility Service {}".format(a.consumer_code, a.utility_service_type))
