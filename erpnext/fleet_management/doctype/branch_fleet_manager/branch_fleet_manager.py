# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BranchFleetManager(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.fleet_management.doctype.branch_fleet_manager_item.branch_fleet_manager_item import BranchFleetManagerItem
		from erpnext.fleet_management.doctype.regular_maintenance_item.regular_maintenance_item import RegularMaintenanceItem
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		item: DF.Table[BranchFleetManagerItem]
		office_name: DF.Data | None
		rm: DF.Table[RegularMaintenanceItem]
	# end: auto-generated types
	def validate(self):
		self.office_name = self.branch
